````markdown
# 🔌 MCP Multi-Source Data Agent

An AI-powered multi-tool assistant built using the **Model Context Protocol (MCP)**, **Google Gemini**, and **Streamlit**.

This project demonstrates how Large Language Models can dynamically discover and use external tools through MCP instead of relying purely on internal knowledge.

---

# 🚀 Features

- 🌤️ Live Weather Information
- 💱 Real-time Currency Conversion
- 📰 Latest News Headlines
- 🔌 MCP-based Tool Architecture
- 🤖 Gemini Function Calling
- ⚡ Async Tool Execution
- 🧠 Dynamic Tool Discovery
- 🛠️ Debuggable Tool Calls
- 🎯 Forced MCP Tool Usage
- 🖥️ Streamlit UI

---

# 🏗️ Architecture

```text
User Query
    │
    ▼
Streamlit Frontend
    │
    ▼
Gemini AI Model
    │
    ▼
MCP Tool Discovery
    │
    ▼
MCP Servers
 ┌─────────────┬─────────────┬─────────────┐
 │ Weather     │ Exchange    │ News        │
 │ Server      │ Server      │ Server      │
 └─────────────┴─────────────┴─────────────┘
    │
    ▼
Tool Response
    │
    ▼
Gemini Final Answer
    │
    ▼
Streamlit Output
````

---

# 📂 Project Structure

```text
.
├── app.py
├── weather_server.py
├── exchange_server.py
├── news_server.py
├── requirements.txt
├── .env
└── README.md
```

---

# 🧠 How MCP Works Here

Instead of hardcoding APIs directly into the chatbot:

1. Each capability is exposed as an MCP server
2. The AI dynamically discovers tools using:

   ```python
   list_tools()
   ```
3. Gemini decides which tool to call
4. MCP executes the tool
5. The tool response is returned back to Gemini
6. Gemini generates the final response

This creates a modular AI-agent architecture.

---

# 🛠️ MCP Tools

## 🌤️ Weather Tool

```python
get_weather(city)
```

### Example

```text
What's the weather in Tokyo?
```

---

## 💱 Currency Conversion Tool

```python
convert_currency(amount, from, to)
```

### Example

```text
Convert 100 USD to INR
```

---

## 📰 News Tool

```python
get_top_headlines(country, category)
```

### Example

```text
Show top technology news in India
```

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone <your_repo_url>
cd <project_folder>
```

---

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Gemini API Setup

Create a Gemini API key from:

[https://aistudio.google.com](https://aistudio.google.com)

---

# 📄 Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

---

# ▶️ Run Application

```bash
streamlit run app.py
```

---

# 💬 Example Queries

```text
What's the weather in Tokyo?
```

```text
Convert 500 USD to EUR
```

```text
Show sports news in India
```

```text
What's the weather in Chennai and convert 100 USD to INR
```

---

# 🔍 MCP Debugging

The application shows:

* Which MCP tool was called
* Tool arguments
* Raw MCP response

This helps verify:

* Gemini is actually using MCP
* No hallucinated answers
* Proper tool orchestration

---

# 📦 requirements.txt

```text
streamlit
python-dotenv
httpx
openai
mcp
```

---

# 🧪 Tech Stack

| Technology | Purpose         |
| ---------- | --------------- |
| Python     | Backend         |
| Streamlit  | Frontend UI     |
| Gemini API | LLM             |
| MCP        | Tool Protocol   |
| AsyncIO    | Async Execution |
| HTTPX      | API Requests    |

---

# 🔥 Key Learning Concepts

This project demonstrates:

* MCP (Model Context Protocol)
* AI Agents
* Tool Calling
* Function Calling
* Async Python
* Multi-tool orchestration
* LLM routing
* Dynamic tool discovery

---

# 🚀 Future Improvements

* Add memory support
* Add vector database
* Add RAG pipeline
* Add authentication
* Add Docker deployment
* Add chat history
* Add voice input
* Add multi-agent collaboration
* Add local LLM support

---

# 📸 Example Workflow

```text
User:
"What's the weather in Tokyo?"

        ↓

Gemini decides:
Call get_weather(city="Tokyo")

        ↓

MCP Weather Server executes

        ↓

Returns weather data

        ↓

Gemini summarizes response

        ↓

Streamlit displays answer
```

---

# 📜 License

MIT License

---

# 🙌 Acknowledgements

Built using:

* Streamlit
* Google Gemini
* Model Context Protocol (MCP)
* Python AsyncIO

---

# ⭐ If You Like This Project

Give it a ⭐ on GitHub and feel free to contribute.

```
```
