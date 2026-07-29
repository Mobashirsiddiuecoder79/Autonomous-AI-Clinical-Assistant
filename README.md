# 🏥 Autonomous AI Clinical Assistant

A production-ready **Autonomous AI Clinical Assistant** built with **Streamlit**, **LangGraph**, **OpenAI**, **SQLAlchemy**, and **FAISS**. The platform assists healthcare professionals by managing patient records, analyzing medical reports, maintaining conversational memory, and providing AI-powered clinical decision support through a modern web interface.

---

# ✨ Features

- 🤖 AI-powered clinical assistant
- 👤 Patient registration and profile management
- 📄 Medical report management
- 💬 Conversational AI with persistent chat history
- 🧠 Long-term semantic memory using FAISS
- 📊 Modern healthcare dashboard
- 📅 Appointment management
- 💊 Medication reminders
- 🔒 Security validation and PII protection
- 🛠 Modular tool execution framework
- 🗄 SQLite database with SQLAlchemy ORM
- 🎨 Modern dark Healthcare SaaS UI

---

# 📷 Application Overview

## Dashboard

- Patient Overview
- Health Summary
- KPI Cards
- Medical Reports
- Appointments
- Medication Reminders
- Recent Activity

## AI Assistant

- Chat with AI
- Clinical reasoning
- Tool execution
- Persistent conversation memory

## Medical Reports

- Upload reports
- Report history
- AI-assisted analysis
- OCR-ready architecture

## Settings

- Database status
- AI Engine status
- Memory status
- System configuration

---

# 🏗 Architecture

The application follows a modular layered architecture.

```
Health-care-Agent/

├── agent/
│   ├── graph.py
│   ├── nodes.py
│   ├── prompts.py
│   └── state.py
│
├── config/
│
├── database/
│   ├── connection.py
│   ├── models.py
│   └── operations.py
│
├── frontend/
│   ├── app.py
│   ├── styles.css
│   │
│   ├── components/
│   │   ├── cards.py
│   │   ├── charts.py
│   │   ├── forms.py
│   │   ├── header.py
│   │   ├── patient.py
│   │   ├── sidebar.py
│   │   ├── tables.py
│   │   └── timeline.py
│   │
│   └── views/
│       ├── dashboard.py
│       ├── chat.py
│       ├── reports.py
│       └── settings.py
│
├── logs/
├── memory/
├── security/
├── tests/
├── tools/
│
├── healthcare_agent.db
├── main.py
├── requirements.txt
└── README.md
```

---

# 🧠 Technology Stack

| Category | Technology |
|----------|------------|
| Frontend | Streamlit |
| AI Framework | LangGraph |
| LLM | OpenAI GPT |
| Database | SQLite + SQLAlchemy |
| Vector Memory | FAISS |
| OCR | Tesseract OCR |
| Styling | Custom CSS |
| Language | Python 3.10+ |

---

# 🚀 Installation

## 1. Clone Repository

```bash
git clone <repository-url>

cd Health-care-Agent
```

---

## 2. Create Virtual Environment

```bash
python3 -m venv venv
```

### macOS / Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
OPENAI_API_KEY=your_openai_api_key

DATABASE_URL=sqlite:///./healthcare_agent.db

ENCRYPTION_KEY=your_generated_key
```

Generate an encryption key:

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

# ▶ Running the Application

Simply execute:

```bash
python3 main.py
```

or directly using Streamlit:

```bash
python3 -m streamlit run frontend/app.py
```

The application opens at

```
http://localhost:8501
```

---

# 📊 Dashboard Features

The dashboard provides:

- Total Patients
- Medical Reports
- AI Sessions
- System Status
- Patient Overview
- Health Summary
- Medical History
- Recent Reports
- Appointments
- Medication Reminders
- Recent Activity

---

# 🤖 AI Assistant

The AI assistant can:

- Answer clinical questions
- Maintain conversation memory
- Retrieve previous interactions
- Execute healthcare tools
- Assist with patient management
- Support report interpretation

---

# 📄 Medical Reports

Supports:

- PDF upload
- Image upload
- OCR-ready parsing
- Report history
- AI report summarization

---

# 🔐 Security

The application includes:

- Prompt injection detection
- Input validation
- Regex sanitization
- PII masking
- Database encryption support

---

# 🧠 Memory System

Three levels of memory:

### Short-Term Memory

- Current conversation
- LangGraph state

### Long-Term Memory

- SQL conversation history
- Patient interactions

### Semantic Memory

- FAISS vector search
- Context retrieval

---

# 🧪 Running Tests

Run the test suite:

```bash
python3 -m pytest tests/
```

The project includes automated tests for:

- Database
- Agent routing
- Memory
- Security
- Tool execution

---

# 📁 Database

Default database:

```
healthcare_agent.db
```

ORM:

- Patient
- Session
- Chat History
- Medical Reports
- Audit Logs
- Tool History

---

# 🎨 User Interface

The application uses a modern Healthcare SaaS interface featuring:

- Dark theme
- Glassmorphism cards
- Responsive layout
- Professional dashboard
- Modern sidebar
- Interactive KPI cards
- AI status indicators

---

# 📌 Future Improvements

- Multi-user authentication
- Doctor dashboard
- Role-based access control
- Real-time notifications
- Voice assistant
- Medical image analysis
- HL7/FHIR integration
- PostgreSQL deployment
- Docker support
- Kubernetes deployment

---

# 👨‍💻 Developed With

- Streamlit
- LangGraph
- OpenAI
- SQLAlchemy
- FAISS
- Python

---

# 📄 License

This project is intended for educational and research purposes.