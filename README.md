# 🏥 Autonomous AI Clinical Assistant v3.1

[🚀 **Live Demo — Try the AI Clinical Assistant**](https://autonomous-ai-clinical-assistant-tpuvax4eqjrmqevuqz88yk.streamlit.app/)

An autonomous AI-powered healthcare assistant built using **LangGraph**, **Google Gemini**, **Streamlit**, **FAISS**, **SQLAlchemy**, and **SQLite**.

The assistant understands user intent, autonomously plans tasks, selects and executes clinical tools, reasons over tool outputs, maintains patient-specific memory, and generates professional healthcare responses.

---

# 🚀 Version

**Current Version:** `v3.1`

---

# ✨ Features

## 🤖 AI & Agent Features

- 🤖 Google Gemini Integration
- 🧠 Autonomous AI Planning
- 🔄 LangGraph Multi-Node Workflow
- 🎯 Intent Detection
- 📋 AI Planner
- 🧩 AI Reasoner
- 🔧 Dynamic Tool Execution
- 💬 Final Answer Generator
- 🔄 Stateful Agent Workflow
- 🛠️ Clinical Tool Routing
- 🧠 Reflection and recovery mechanisms

## 👤 Patient Management

- 👤 Patient-specific healthcare profiles
- 🗂️ Patient memory management
- 🔐 Patient data isolation
- 📊 Patient dashboard
- 📄 Medical report management
- 💬 Patient-specific AI sessions
- 🧬 Patient clinical history

## 🔐 Authentication

- 🔑 Google OAuth / OpenID Connect authentication
- 👤 Automatic patient-account creation for new authenticated users
- 📧 Google account email mapped to patient email
- 🔒 Authenticated users can access only their linked patient profile
- 🚪 Secure sign-out
- 🆕 New Google users can create their healthcare profile after authentication
- 🔗 Existing patients are automatically linked when their patient email matches their authenticated Google email

## 🏥 Clinical Features

- 📚 FAISS Vector Memory
- 📄 Medical Report Parsing
- 🧪 Laboratory Report Analysis
- 💊 Drug Interaction Checker
- ⚖️ BMI Calculator
- 🩺 Symptom Assessment
- 📅 Appointment Scheduling
- 🧠 Clinical context retrieval

## 🌐 Web Application

- 🎨 Streamlit Web Interface
- 📊 Clinical Dashboard
- 👤 Patient Overview
- 📋 Reports Dashboard
- 💬 AI Assistant Interface
- ⚙️ Patient Settings
- 🔐 Authentication-protected application

---

# 🏗️ System Architecture

```text
                         ┌───────────────────┐
                         │   Google Login    │
                         │     OAuth/OIDC    │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │ Authentication    │
                         │ & Patient Mapping │
                         └─────────┬─────────┘
                                   │
                         ┌─────────▼─────────┐
                         │ Healthcare        │
                         │ Patient Profile   │
                         └─────────┬─────────┘
                                   │
                                   ▼
                              User Query
                                   │
                                   ▼
                         ┌───────────────────┐
                         │ Intent Detector   │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │    AI Planner     │
                         └─────────┬─────────┘
                                   │
                         ┌─────────▼─────────┐
                         │   Need Tool?      │
                         └──────┬──────┬─────┘
                                │      │
                              No│      │Yes
                                │      │
                                │      ▼
                                │ ┌───────────────┐
                                │ │ AI Reasoner   │
                                │ └───────┬───────┘
                                │         │
                                │         ▼
                                │ ┌───────────────┐
                                │ │ Tool Executor │
                                │ └───────┬───────┘
                                │         │
                                │         ▼
                                │ ┌───────────────┐
                                │ │ AI Reasoner   │
                                │ └───────┬───────┘
                                │         │
                                └─────────┴───────┐
                                                  ▼
                                         ┌────────────────┐
                                         │ Final Answer   │
                                         └────────────────┘
```

---

# 🔐 Authentication Architecture

The application uses Google authentication through Streamlit’s authentication system.

The authenticated Google email is used to identify the corresponding healthcare patient.

```text
Google Account
      │
      ▼
Google OAuth / OIDC
      │
      ▼
Authenticated Email
      │
      ▼
Search Patient.email
      │
      ├───────────────┐
      │               │
      ▼               ▼
Existing Patient   No Patient
      │               │
      │               ▼
      │       Create Healthcare
      │           Profile
      │               │
      └───────┬───────┘
              ▼
       Active Patient
              │
              ▼
       Healthcare Dashboard
```

## Existing Patient

If the authenticated Google email matches an existing patient email:

Google Email == Patient.email

The existing patient profile is loaded automatically.

New Google User

If the authenticated Google email does not exist in the patient database, the application displays:

Create Your Healthcare Profile

The user provides:

* First Name
* Last Name
* Date of Birth
* Gender

The application then creates a new patient record using the authenticated Google email.

---

# 🛡️ Authentication Security

The application does not hardcode the authenticated user’s email.

The email is obtained from the authenticated identity provider.

Patient authorization follows:

```text
Authenticated Google Email
            │
            ▼
       Patient.email
            │
            ▼
      Patient Record
```

If authentication succeeds but no patient record exists, the application allows the authenticated user to create their healthcare profile.

⸻

📂 Project Structure

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
│   ├── connection.py
│   ├── models.py
│   └── operations.py
│
├── frontend/
│   ├── app.py
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   └── authentication.py
│   │
│   ├── components/
│   │   ├── cards.py
│   │   ├── header.py
│   │   ├── patient.py
│   │   └── sidebar.py
│   │
│   └── views/
│       ├── dashboard.py
│       ├── chat.py
│       ├── reports.py
│       └── user_settings.py
│
├── memory/
├── security/
├── tools/
├── tests/
├── logs/
├── requirements.txt
└── main.py

# ⚙️ Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Application Backend |
| LangGraph | Stateful AI Workflow Engine |
| LangChain | LLM Integration |
| Google Gemini | AI Reasoning |
| Streamlit | Web Application |
| SQLite | Relational Database |
| SQLAlchemy | Database ORM |
| FAISS | Vector Memory |
| Authlib | OAuth / Authentication Support |
| Pydantic | Data Validation |

🧠 AI Workflow

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
 ┌───┴────┐
 │        │
No       Yes
 │        │
 ▼        ▼
Final   AI Reasoner
Answer      │
            ▼
      Tool Executor
            │
            ▼
       Tool Result
            │
            ▼
        AI Reasoner
            │
            ▼
       Final Answer

🔧 Available Clinical Tools

The application provides clinical and healthcare-support utilities including:

* ⚖️ BMI Calculator
* 💊 Drug Interaction Checker
* 🩺 Symptom Assessment
* 📅 Appointment Scheduler
* 🧪 Laboratory Report Analyzer
* 📄 Medical Report Parser
* 🔎 Clinical Information Retrieval
* 🧠 Patient Memory Retrieval

⸻

💾 Database

The application uses SQLite with SQLAlchemy.

The primary patient model contains:

Patient
├── id
├── first_name
├── last_name
├── email
├── encrypted_ssn
├── date_of_birth
├── gender
├── medical_history
└── created_at

Additional database entities include:

Patient
   │
   ├── Sessions
   │      ├── Chat History
   │      └── Tool History
   │
   └── Medical Reports

Patient email addresses are unique in the database.

This allows the authentication layer to map one authenticated Google account to its corresponding patient profile.

⸻

🧠 Patient Memory

Patient-specific information can be stored and retrieved through:

SQLite
   │
   ├── Patient Profile
   ├── Sessions
   ├── Chat History
   ├── Medical Reports
   └── Tool History

and 

FAISS
   │
   └── Patient-specific Vector Memory

This allows the AI assistant to retrieve relevant historical context during conversations.

⸻

🔒 Security Features

* 🔑 Google OAuth / OIDC Authentication
* 👤 Patient Identity Mapping
* 🔐 Patient Data Isolation
* 🛡️ Prompt Injection Detection
* 🧹 Input Sanitization
* 🔒 Secure Conversation Memory
* 🔐 Environment-based API Key Configuration
* 🧾 Audit Logging
* 🔏 Sensitive Data Protection
* 📧 Authenticated Email Validation

⸻

💻 Installation

1. Clone the Repository

git clone https://github.com/Mobashirsiddiuecoder79/Autonomous-AI-Clinical-Assistant.git

2. Enter the Project

cd Autonomous-AI-Clinical-Assistant

3. Create a Virtual Environment

python3 -m venv .venv

Activate it on macOS/Linux:

source .venv/bin/activate

Activate it on Windows:

.venv\Scripts\activate

4. Install Dependencies

pip install -r requirements.txt

🔑 Environment Configuration

Create a .env file for local application configuration.

GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-3.6-flash

DATABASE_URL=sqlite:///./healthcare_agent.db

LOG_LEVEL=INFO

Do not commit API keys, OAuth client secrets, or other credentials to GitHub.

⸻

🔐 Google Authentication Configuration

The application uses Streamlit authentication with Google as the OpenID Connect provider.

For local development, the OAuth redirect URI is:

http://localhost:8501/oauth2callback

For Streamlit Cloud deployment:

https://YOUR-APP-NAME.streamlit.app/oauth2callback

The OAuth redirect URI configured in Google Cloud Console must exactly match the URI configured for the corresponding environment.

⸻

☁️ Streamlit Cloud Deployment

The application can be deployed using Streamlit Cloud.

Main Application File

Configure Streamlit Cloud to use:

frontend/app.py

Streamlit Secrets

For deployment, configure the following secrets in Streamlit Cloud:

[auth]
redirect_uri = "https://YOUR-APP-NAME.streamlit.app/oauth2callback"
cookie_secret = "YOUR_EXISTING_COOKIE_SECRET"
client_id = "YOUR_GOOGLE_CLIENT_ID"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

Replace the placeholder values with the actual deployment credentials.

Never commit client_secret or cookie_secret to GitHub.

⸻

🌐 OAuth Redirect URIs

Local Development

http://localhost:8501/oauth2callback

Streamlit Cloud

https://YOUR-APP-NAME.streamlit.app/oauth2callback

The URI configured in Google Cloud Console and Streamlit Cloud must match exactly.

⸻

▶️ Run Locally

Start Streamlit:

python3 -m streamlit run frontend/app.py

Or

streamlit run frontend/app.py

The application will normally be available at:

http://localhost:8501

👤 First Login

When a user opens the application:

Application
     │
     ▼
Continue with Google
     │
     ▼
Google Authentication
     │
     ▼
Authenticated
     │
     ▼
Patient Found?
     │
 ┌───┴────┐
 │        │
Yes      No
 │        │
 ▼        ▼
Open    Create
Dashboard Profile

Existing User

If the Google email already exists in the patient database, the existing healthcare profile is loaded automatically.

New User

If the Google email does not exist, the user is asked to create a healthcare profile with:

* First Name
* Last Name
* Date of Birth
* Gender

The authenticated Google email is automatically used as the patient’s email.

⸻

💬 Example Queries

General Questions

* What is diabetes?
* What causes high blood pressure?
* Explain asthma.

BMI

* Calculate BMI for 70 kg and 175 cm.

Drug Interaction

* Can I take Aspirin with Warfarin?

Symptom Assessment

* I have chest pain and difficulty breathing.

Appointment

* Book an appointment for tomorrow morning.

Medical Reports

* Analyze my blood report.
* Summarize this medical report.

⸻

📊 Dashboard

The dashboard provides an overview of the authenticated patient’s healthcare information.

The interface includes:

* 👤 Active Patient
* 📋 Patient Overview
* ❤️ Health Summary
* 📄 Medical Reports
* 💬 AI Sessions
* 🟢 System Status
* 🤖 AI Assistant
* 🧪 Laboratory Reports
* ⚙️ Patient Settings

Each authenticated user is associated with their own active patient profile.

⸻

🧪 Testing

Run the test suite:
pytest

Run tests from the tests directory:
pytest tests/


📈 Current Development Status

✅ Version 3.1

Completed:

* Modular LangGraph Architecture
* Gemini Integration
* AI Planner
* AI Reasoner
* Tool Executor
* Final Answer Generator
* Dynamic Routing
* Memory Integration
* Patient Database
* Patient-specific Sessions
* Medical Report Management
* FAISS Vector Memory
* Streamlit Dashboard
* Google OAuth / OIDC Authentication
* Automatic Healthcare Profile Creation
* Google Account → Patient Email Mapping
* Patient Data Isolation
* User Settings
* Streamlit Cloud Deployment

⸻

🚀 Roadmap

Version 3.2

* Reflection Agent Improvements
* Self-Correction
* Improved Clinical Validation
* Confidence Scoring
* Improved Error Recovery
* Enhanced Patient Memory

Version 4.0

* Multi-Agent Collaboration
* Doctor Dashboard
* Clinical RAG Knowledge Base
* Advanced Medical Document Processing
* PostgreSQL Production Database
* Docker Deployment
* CI/CD Pipeline
* Advanced Monitoring

⸻

⚠️ Medical Disclaimer

This project is intended for educational and research purposes.

The AI Clinical Assistant is a decision-support and information system. It does not replace qualified medical professionals, clinical judgment, diagnosis, treatment, or emergency medical services.

Users should consult a qualified healthcare professional for medical decisions.

⸻

📄 License

This project is intended for educational and research purposes.

The assistant does not replace professional medical advice, diagnosis, or treatment.
EOF



