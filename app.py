import streamlit as st
import asyncio
import json
import os
from dotenv import load_dotenv
import httpx

from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

# =========================================================
# STREAMLIT CONFIG
# =========================================================

st.set_page_config(
    page_title="MCP Multi-Source Agent",
    page_icon="🔌"
)

st.title("🔌 MCP Multi-Source Data Agent")

st.markdown("""
This AI agent uses the **Model Context Protocol (MCP)** to connect to:

- 🌤️ Weather Server
- 💱 Exchange Server
- 📰 News Server
""")

with st.sidebar:

    st.header("📡 Available MCP Servers")

    st.markdown("""
- 🌤️ `get_weather(city)`
- 💱 `convert_currency(amount, from, to)`
- 📰 `get_top_headlines(country, category)`
""")

# =========================================================
# MAIN QUERY FUNCTION
# =========================================================

async def process_query(user_query):

    # =====================================================
    # GEMINI API KEY
    # =====================================================

    gemini_api_key = os.environ.get(
        "GEMINI_API_KEY"
    )

    if gemini_api_key:
        gemini_api_key = gemini_api_key.strip()

    if not gemini_api_key:
        return "❌ GEMINI_API_KEY not found in .env"

    # =====================================================
    # GEMINI CLIENT
    # =====================================================

    provider = "Google Gemini"

    client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url=(
            "https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    )

    provider_url = (
        "https://generativelanguage.googleapis.com/v1beta/models"
    )

    candidate_models = [

        "gemini-2.5-flash",

        "gemini-2.0-flash",

        "gemini-1.5-flash"
    ]

    # =====================================================
    # CONNECTIVITY TEST
    # =====================================================

    try:

        async with httpx.AsyncClient(
            timeout=15.0
        ) as http_client:

            response = await http_client.get(
                provider_url,
                headers={
                    "x-goog-api-key":
                    gemini_api_key
                }
            )

        if response.status_code == 200:

            st.success(
                f"✅ {provider} connectivity OK"
            )

        else:

            st.warning(
                f"⚠️ {provider} returned "
                f"HTTP {response.status_code}"
            )

            try:
                st.json(response.json())
            except:
                st.write(response.text)

    except Exception as e:

        st.error(
            f"{provider} connectivity failed"
        )

        st.error(str(e))

        return (
            f"❌ Cannot connect to {provider}"
        )

    # =====================================================
    # MCP SERVERS
    # =====================================================

    servers = {

        "weather": StdioServerParameters(
            command="python",
            args=["weather_server.py"]
        ),

        "exchange": StdioServerParameters(
            command="python",
            args=["exchange_server.py"]
        ),

        "news": StdioServerParameters(
            command="python",
            args=["news_server.py"]
        ),
    }

    openai_tools = []
    tool_to_session = {}

    exit_stack = AsyncExitStack()

    # =====================================================
    # CONNECT TO MCP SERVERS
    # =====================================================

    for server_name, server_params in servers.items():

        try:

            st.info(
                f"Connecting to {server_name} server..."
            )

            transport = (
                await exit_stack.enter_async_context(
                    stdio_client(server_params)
                )
            )

            read, write = transport

            session = (
                await exit_stack.enter_async_context(
                    ClientSession(read, write)
                )
            )

            await session.initialize()

            tools_response = (
                await session.list_tools()
            )

            st.success(
                f"✅ {server_name}: "
                f"{len(tools_response.tools)} tool(s)"
            )

            for tool in tools_response.tools:

                openai_tools.append({

                    "type": "function",

                    "function": {

                        "name": tool.name,

                        "description":
                        tool.description or "",

                        "parameters":
                        tool.inputSchema
                    }
                })

                tool_to_session[
                    tool.name
                ] = session

        except Exception as e:

            st.warning(
                f"⚠️ Failed connecting "
                f"to {server_name}: {e}"
            )

    if not openai_tools:

        await exit_stack.aclose()

        return "❌ No MCP tools available."

    # =====================================================
    # SYSTEM PROMPT
    # =====================================================

    SYSTEM_PROMPT = """
You are an MCP-powered AI assistant.

IMPORTANT RULES:

1. For weather-related questions:
   ALWAYS use the get_weather tool.

2. For currency conversion:
   ALWAYS use the convert_currency tool.

3. For news or headlines:
   ALWAYS use the get_top_headlines tool.

4. NEVER answer weather, news,
   or exchange questions from
   your internal knowledge.

5. ALWAYS prefer MCP tools
   over internal knowledge.

6. If a matching MCP tool exists,
   you MUST call the tool first.

7. After receiving tool output,
   summarize it naturally for the user.
"""

    # =====================================================
    # CHAT LOOP
    # =====================================================

    try:

        messages = [

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": user_query
            }
        ]

        response = None
        selected_model = None

        # =================================================
        # MODEL FALLBACK LOOP
        # =================================================

        for model_name in candidate_models:

            try:

                st.info(
                    f"Trying model: {model_name}"
                )

                response = (
                    await client.chat.completions.create(

                        model=model_name,

                        messages=messages,

                        tools=openai_tools,

                        tool_choice="auto"
                    )
                )

                selected_model = model_name

                st.success(
                    f"✅ Using model: "
                    f"{selected_model}"
                )

                break

            except Exception as e:

                st.warning(
                    f"⚠️ Model failed: "
                    f"{model_name}\n\n{e}"
                )

                await asyncio.sleep(2)

        if response is None:

            return "❌ All Gemini models failed."

        assistant_message = (
            response.choices[0].message
        )

        # =================================================
        # TOOL LOOP
        # =================================================

        while assistant_message.tool_calls:

            messages.append(assistant_message)

            for tool_call in (
                assistant_message.tool_calls
            ):

                tool_name = (
                    tool_call.function.name
                )

                tool_args = json.loads(
                    tool_call.function.arguments
                )

                # =========================================
                # TOOL DEBUGGING
                # =========================================

                st.write(
                    f"### 🔧 TOOL USED: {tool_name}"
                )

                st.json(tool_args)

                session = tool_to_session.get(
                    tool_name
                )

                # =========================================
                # TOOL EXECUTION
                # =========================================

                if not session:

                    tool_result_text = (
                        f"Tool '{tool_name}' "
                        f"not found."
                    )

                else:

                    try:

                        result = await session.call_tool(
                            tool_name,
                            tool_args
                        )

                        tool_result_text = "\n".join(

                            getattr(c, "text", str(c))

                            for c in result.content
                        )

                        st.success(
                            f"✅ {tool_name} completed"
                        )

                        # =================================
                        # SHOW RAW MCP RESPONSE
                        # =================================

                        st.code(
                            tool_result_text,
                            language="text"
                        )

                    except Exception as e:

                        tool_result_text = (
                            f"Tool execution error: {e}"
                        )

                messages.append({

                    "role": "tool",

                    "tool_call_id":
                    tool_call.id,

                    "content":
                    tool_result_text
                })

            # =============================================
            # FOLLOW-UP MODEL RESPONSE
            # =============================================

            response = (
                await client.chat.completions.create(

                    model=selected_model,

                    messages=messages,

                    tools=openai_tools,

                    tool_choice="auto"
                )
            )

            assistant_message = (
                response.choices[0].message
            )

        return assistant_message.content

    finally:

        await exit_stack.aclose()

# =========================================================
# STREAMLIT UI
# =========================================================

user_input = st.text_input(
    "Ask me anything:",
    placeholder=(
        "What's the weather in Tokyo?"
    )
)

if st.button("Ask AI"):

    if not user_input:

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner("Thinking..."):

            try:

                loop = asyncio.new_event_loop()

                asyncio.set_event_loop(loop)

                result = loop.run_until_complete(
                    process_query(user_input)
                )

                st.markdown("### Response")

                st.write(result)

            except Exception as e:

                st.error(str(e))
                st.error(type(e).__name__)
