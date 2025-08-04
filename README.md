# 📞 AI-Powered Sales Call Automation (FastAPI Backend)

This is a FastAPI-based backend for a **B2B platform** that wraps around **Bland.AI** to automate sales outreach via intelligent voice agents. Businesses can submit product and client details through a user-friendly frontend, and AI agents will handle the initial contact with clients.

---

## 🚀 Overview

The platform enables businesses to:
- Submit their **business name**, **product details**, and **client list** via a simple form.
- Automatically trigger AI voice agents (powered by Bland) to call the clients and pitch the product.

### 🤖 Call Flow Logic
- ✅ **Positive Reaction** → Client is handed off to a **human sales agent** for follow-up.
- ❌ **Negative Reaction** → No further action; client is dropped.
- ⚠️ **Neutral Reaction** → AI follows up again later with another attempt.

This system helps optimize lead conversion by combining **AI efficiency** with **human intuition**.

---

## 🧱 Project Structure

```
.
├── app/
│   ├── api/               # API route definitions (auth, campaigns, contacts, calls)
│   ├── core/              # Config, DB setup, templates, dependencies
│   ├── crud/              # Database operations (create, read, update)
│   ├── models/            # SQLAlchemy model definitions
│   ├── schemas/           # Pydantic data schemas
│   ├── services/          # Business logic (call agents, schedulers, TTS, etc.)
│   ├── utils/             # Utility functions (e.g., authentication)
│   ├── static/            # Static files like CSS
│   ├── templates/         # HTML templates (e.g., index.html)
│   ├── main.py            # FastAPI entrypoint
│   └── LLM_model/         # Local LLM model file (Mistral .gguf)
├── .env                   # Environment variables
├── Dockerfile             # Docker container configuration
├── render.yaml            # Deployment configuration (Render.com or similar)
├── requirements.txt       # Python dependencies
├── setup.py               # Python package metadata
```

---

## 🛠️ Tech Stack

- **FastAPI** – High-performance Python web framework
- **SQLAlchemy** – ORM for database operations
- **Pydantic** – Data validation and parsing
- **Celery** – Asynchronous task scheduling
- **Docker** – Containerized deployment
- **Bland.AI** – AI voice agent integration
- **Mistral-7B GGUF** – Local language model (optional use)

---

## 🧪 Setup & Run (Development)

1. **Clone the repo**
   ```bash
   git clone https://github.com/zatiyab/AI-Call-Salesman.git
   cd AI-Call-Salesman
   ```

2. **Create virtual environment & activate**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run FastAPI server**
   ```bash
   uvicorn app.main:app --reload
   ```

---

## 📦 Deployment

- Deployment can be configured via `Dockerfile` and `render.yaml`.
- CI/CD is managed using GitHub Actions (`.github/workflows/deploy.yml`).

---

## 🧠 Future Plans

- Add dashboard analytics for call success/failure rates.
- Fine-tune call responses with LLM (using Mistral or similar).
- Add admin panel for campaign tracking.

---

## 🤝 Contributing

Pull requests are welcome! If you’d like to contribute:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature-x`)
3. Push changes and open a PR

---

## 📄 License

This project is licensed under the MIT License.

---

## 📬 Contact

For questions, suggestions, or demo requests:  
📧 aliatiyab.husain@gmail.com 
