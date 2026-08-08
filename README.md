# 🏥 Autonomous AI Clinical Assistant v3.0

[🚀 **Live Demo — Try the AI Clinical Assistant**](https://autonomous-ai-clinical-assistant-tpuvax4eqjrmqevuqz88yk.streamlit.app/)

An autonomous AI-powered healthcare assistant built using **LangGraph**, **Google Gemini**, **Streamlit**, **FAISS**, and **SQLite**.

# 🏥 Autonomous AI Clinical Assistant v3.0

An autonomous AI-powered healthcare assistant built using **LangGraph**, **Google Gemini 3.6 Flash**, **Streamlit**, **FAISS**, and **SQLite**.

The assistant understands user intent, autonomously plans tasks, selects and executes clinical tools, reasons over tool outputs, and generates professional healthcare responses.

---

# 🚀 Version

**Current Version:** `v3.0`

---

# ✨ Features

- 🤖 Google Gemini 3.6 Flash Integration
- 🧠 Autonomous AI Planning
- 🔄 LangGraph Multi-Node Workflow
- 🎯 Intent Detection
- 📋 AI Planner
- 🧩 AI Reasoner
- 🔧 Dynamic Tool Execution
- 💬 Final Answer Generator
- 🗂️ Patient Memory Management
- 📚 FAISS Vector Memory
- 🔒 Input Sanitization
- 📄 Medical Report Parsing
- 💊 Drug Interaction Checker
- ⚖️ BMI Calculator
- 🩺 Symptom Assessment
- 📅 Appointment Scheduling
- 🌐 Streamlit Web Interface

---

# 🏗️ System Architecture

```
                 User
                  │
                  ▼
        Intent Detector
                  │
                  ▼
             AI Planner
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
   Direct Answer      Tool Required
        │                   │
        │                   ▼
        │             AI Reasoner
        │                   │
        │                   ▼
        │            Tool Executor
        │                   │
        │                   ▼
        │             AI Reasoner
        │                   │
        └──────────► Final Answer
```

---

# 📂 Project Structure

```
Health-care-Agent/

├── agent/
│   ├── graph.py
│   ├── state.py
│   ├── edges.py
│   ├── legacy_nodes.py
│   └── nodes/
│       ├── intent.py
│       ├── planner.py
│       ├── reasoner.py
│       ├── tool_executor.py
│       ├── final_answer.py
│       └── reflector.py
│
├── config/
│   ├── llm.py
│   └── settings.py
│
├── database/
├── frontend/
├── memory/
├── security/
├── tools/
├── tests/
├── logs/
├── requirements.txt
└── main.py
```

---

# ⚙️ Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend |
| LangGraph | AI Workflow Engine |
| LangChain | LLM Integration |
| Gemini 3.6 Flash | AI Reasoning |
| Streamlit | Web UI |
| SQLite | Database |
| FAISS | Vector Memory |
| SQLAlchemy | ORM |
| Pydantic | Data Validation |

---

# 🧠 Workflow

```
User Query
      │
      ▼
Intent Detection
      │
      ▼
AI Planner
      │
      ▼
Need Tool?
      │
 ┌────┴────┐
 │         │
No        Yes
 │         │
 ▼         ▼
Final   AI Reasoner
Answer      │
            ▼
     Tool Executor
            │
            ▼
      AI Reasoner
            │
            ▼
      Final Answer
```

---

# 🔧 Available Clinical Tools

- BMI Calculator
- Drug Interaction Checker
- Symptom Assessment
- Appointment Scheduler
- Laboratory Report Analyzer
- Medical Report Parser

---

# 💻 Installation

Clone the repository

```bash
git clone https://github.com/Mobashirsiddiuecoder79/Autonomous-AI-Clinical-Assistant.git
```

Enter the project

```bash
cd Autonomous-AI-Clinical-Assistant
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-3.6-flash

DATABASE_URL=sqlite:///./healthcare_agent.db

LOG_LEVEL=INFO
```

Run the application

```bash
python3 -m streamlit run frontend/app.py \
    --server.runOnSave true \
    --server.fileWatcherType auto
```
or 

```bash
python3 -m streamlit run frontend/app.py
```


---

# 💬 Example Queries

### General Questions

- What is diabetes?
- What causes high blood pressure?
- Explain asthma.

### BMI

- Calculate BMI for 70 kg and 175 cm.

### Drug Interaction

- Can I take Aspirin with Warfarin?

### Symptom Assessment

- I have chest pain and difficulty breathing.

### Appointment

- Book an appointment for tomorrow morning.

### Medical Reports

- Analyze my blood report.
- Summarize this medical report.

---

# 🔒 Security Features

- Prompt Injection Detection
- Input Sanitization
- Patient Data Isolation
- Secure Conversation Memory
- API Key Environment Configuration

---

# 📈 Current Development Status

## ✅ Version 3.0

Completed

- Modular LangGraph Architecture
- Gemini Integration
- AI Planner
- AI Reasoner
- Tool Executor
- Final Answer Generator
- Dynamic Routing
- Memory Integration
- Logging
- Streamlit Interface

---

# 🚀 Roadmap

## Version 4.0

- Reflection Agent
- Self-Correction
- Multi-Agent Collaboration
- Clinical Validation
- Confidence Scoring

## Version 5.0

- Doctor Dashboard
- Authentication
- RAG Knowledge Base
- Docker Deployment
- CI/CD Pipeline
- Cloud Deployment

---

# 📄 License

This project is intended for educational and research purposes.

The assistant does **not** replace professional medical advice, diagnosis, or treatment.

---

# 👨‍💻 Author

**Md Mobashir Imam**

B.Tech Computer Science & Engineering

National Institute of Technology Patna

---

⭐ If you found this project useful, consider giving it a star on GitHub.
