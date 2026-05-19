# 🔌 MCP Multi-Source Data Agent

An AI-powered assistant built using:

- MCP (Model Context Protocol)
- Google Gemini
- Streamlit

This project demonstrates how LLMs can dynamically discover and use external tools through MCP instead of relying only on internal knowledge.

---

## 🚀 Features

- 🌤️ Live Weather Information
- 💱 Currency Conversion
- 📰 Latest News Headlines
- 🔌 MCP-based Tool Architecture
- 🤖 Gemini Function Calling
- ⚡ Async Tool Execution
- 🧠 Dynamic Tool Discovery
- 🛠️ MCP Tool Debugging
- 🖥️ Streamlit UI

---

## 🏗️ Architecture

```text
User Query
    ↓
Streamlit UI
    ↓
Gemini AI
    ↓
MCP Tool Selection
    ↓
MCP Servers
 ├── Weather Server
 ├── Exchange Server
 └── News Server
    ↓
Tool Response
    ↓
Gemini Final Answer
```

---

## 📂 Project Structure

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

## 🧠 How It Works

1. Streamlit launches the UI.
2. MCP servers start using stdio transport.
3. Gemini dynamically discovers available tools.
4. Gemini decides which tool to call.
5. MCP executes the tool.
6. Tool response is returned to Gemini.
7. Final answer is displayed in Streamlit.

---

## 🛠️ MCP Tools

### 🌤️ Weather Tool

```python
get_weather(city)
```

Example:

```text
What's the weather in Tokyo?
```

---

### 💱 Currency Conversion Tool

```python
convert_currency(amount, from, to)
```

Example:

```text
Convert 100 USD to INR
```

---

### 📰 News Tool

```python
get_top_headlines(country, category)
```

Example:

```text
Show top technology news in India
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone <your_repo_url>
cd <project_folder>
```

---

### 2. Create Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Gemini API Setup

Get your API key from:

https://aistudio.google.com

---

## 📄 .env File

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

---

## 💬 Example Queries

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

## 🔍 MCP Debugging

The app displays:

- Tool name used
- Tool arguments
- Raw MCP response

This helps verify that Gemini is actually using MCP tools.

---

## 📦 requirements.txt

```text
streamlit
python-dotenv
httpx
openai
mcp
```

---

## 🧪 Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend |
| Streamlit | Frontend |
| Gemini API | LLM |
| MCP | Tool Protocol |
| AsyncIO | Async Execution |
| HTTPX | API Requests |

---

## 🚀 Future Improvements

- Add memory support
- Add vector database
- Add RAG pipeline
- Add Docker deployment
- Add authentication
- Add voice input
- Add multi-agent support

---

## 📜 License

MIT License

---

## ⭐ Support

If you like this project, give it a star on GitHub.
