import streamlit as st
import asyncio
import json
import os
from dotenv import load_dotenv
load_dotenv()
import httpx
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack

st.set_page_config(page_title="MCP Multi-Source Agent", page_icon="🔌")
st.title("🔌 MCP Multi-Source Data Agent")

st.markdown("""
This AI agent uses the **Model Context Protocol (MCP)** to connect to 
three independent tool servers: Weather, Exchange Rates, and News.
""")

with st.sidebar:
    st.header("📡 Available MCP Servers")
    st.markdown("""
    - 🌤️ **Weather Server** - `get_weather(city)`
    - 💱 **Exchange Server** - `convert_currency(amount, from, to)`
    - 📰 **News Server** - `get_top_headlines(country, category)`
    """)
    st.divider()
    st.markdown("*Tools are auto-discovered via MCP's `list_tools()`*")

async def process_query(user_query):
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        return "❌ Error: OPENROUTER_API_KEY not found in .env file."

    client = OpenAI(
        api_key=openrouter_api_key,
        base_url="https://api.openrouter.ai/v1"
    )

    try:
        test_resp = httpx.get(
            "https://api.openrouter.ai/v1/models",
            headers={"Authorization": f"Bearer {openrouter_api_key}"},
            timeout=10.0,
        )
        st.info(f"OpenRouter connectivity test: {test_resp.status_code} {test_resp.reason_phrase}")
    except httpx.ConnectError as e:
        st.error("OpenRouter connectivity test failed: unable to resolve or connect to api.openrouter.ai.")
        st.error("This looks like a Codespaces network/DNS restriction rather than a model issue.")
        st.error(f"ConnectError: {e}")
        return "❌ Cannot reach OpenRouter from this environment. Check Codespaces outbound network, DNS, or proxy settings."
    except Exception as e:
        st.error(f"OpenRouter connectivity test failed: {type(e).__name__}: {e}")
        return f"❌ OpenRouter connectivity test failed: {type(e).__name__}: {e}"

    openrouter_model = os.environ.get("OPENROUTER_MODEL") or "meta-llama/llama-3.3-70b-instruct:free"
    candidate_models = [
        openrouter_model,
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4o-rev",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k"
    ]
    candidate_models = [m for i, m in enumerate(candidate_models) if m not in candidate_models[:i]]

    st.info(f"Using OpenRouter model: auto-detecting from {candidate_models[0]} first...")
    
    servers = {
        "weather": StdioServerParameters(command="python3", args=["weather_server.py"]),
        "exchange": StdioServerParameters(command="python3", args=["exchange_server.py"]),
        "news": StdioServerParameters(command="python3", args=["news_server.py"]),
    }
    
    openai_tools = []
    tool_to_session = {}
    exit_stack = AsyncExitStack()
    
    for server_name, server_params in servers.items():
        try:
            st.info(f"Connecting to {server_name} server...")
            
            # Use AsyncExitStack for proper async context management
            stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
            read, write = stdio_transport
            
            session = await exit_stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            
            tools_response = await session.list_tools()
            server_tools = tools_response.tools
            st.success(f"✅ {server_name}: Found {len(server_tools)} tool(s)")
            
            for tool in server_tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.inputSchema
                    }
                })
                tool_to_session[tool.name] = session
                
        except Exception as e:
            st.warning(f"⚠️ Could not connect to {server_name}: {str(e)}")
    
    if not openai_tools:
        await exit_stack.aclose()
        return "❌ No MCP servers are available."
    
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use the available tools to answer questions."},
            {"role": "user", "content": user_query}
        ]

        response = None
        last_error = None
        model_errors = []
        for candidate in candidate_models:
            try:
                st.info(f"Trying OpenRouter model: {candidate}")
                response = client.chat.completions.create(
                    model=candidate,
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto"
                )
                openrouter_model = candidate
                break
            except Exception as e:
                error_info = f"{e.__class__.__name__}: {repr(e)}"
                model_errors.append((candidate, error_info))
                st.warning(f"Model {candidate} failed: {error_info}")
                err_text = str(e).lower()
                if "model not found" in err_text or "invalid argument" in err_text:
                    last_error = e
                    continue
                raise

        if response is None:
            error_details = " | ".join([f"{m}: {err}" for m, err in model_errors])
            raise RuntimeError(f"No valid OpenRouter model could be selected. Tried: {candidate_models}. Errors: {error_details}")

        st.info(f"Using OpenRouter model: {openrouter_model}")
        assistant_message = response.choices[0].message
        
        while assistant_message.tool_calls:
            st.info(f"🤖 Tool call in progress: {len(assistant_message.tool_calls)} tool(s)...")
            messages.append(assistant_message)
            
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                session = tool_to_session.get(tool_name)
                
                if session:
                    result = await session.call_tool(tool_name, tool_args)
                    tool_result_text = result.content[0].text
                    st.success(f"✅ {tool_name}: {tool_result_text[:100]}...")
                else:
                    tool_result_text = f"Error: Tool '{tool_name}' not found."
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result_text
                })
            
            try:
                response = client.chat.completions.create(
                    model=openrouter_model,
                    messages=messages
                )
                assistant_message = response.choices[0].message
            except Exception as e:
                error_info = f"{e.__class__.__name__}: {repr(e)}"
                st.error(f"Follow-up chat call failed with {error_info}")
                raise
        
        return assistant_message.content
        
    finally:
        # Properly close all connections
        await exit_stack.aclose()

# UI
user_input = st.text_input(
    "Ask me anything:",
    placeholder="e.g., What's the weather in Tokyo, convert 100 USD to JPY, and show top tech news"
)

if st.button("Ask AI", type="primary"):
    if user_input:
        with st.spinner("Thinking..."):
            try:
                result = asyncio.run(process_query(user_input))
                st.markdown("### Response:")
                st.markdown(result)
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.error(f"Exception type: {e.__class__.__name__}")
                st.error(f"Exception repr: {repr(e)}")
    else:
        st.warning("Please type a question first.")