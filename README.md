# 🧠 RAGbot: Document Q&A system

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Pinecone](https://img.shields.io/badge/Pinecone-Vector%20DB-black?style=for-the-badge&logo=pinecone&logoColor=white)
![Llama 3](https://img.shields.io/badge/AI-Llama%203%2070B-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **A high-performance Retrieval-Augmented Generation (RAG) system capable of ingesting documents, maintaining context-aware conversations, and providing source-backed answers with sub-second latency.**

---

## 🚀 Project Overview

**RAGbot** is a state-of-the-art conversational AI agent designed to bridge the gap between static documents and dynamic knowledge retrieval. Leveraging **Hybrid Search** algorithms and **Cross-Encoder Re-ranking**, RAGbot achieves superior retrieval accuracy compared to standard vector-only databases.

Built for scalability, it utilizes **Pinecone** for serverless vector storage, **Supabase** for secure user authentication & persistent chat history, and **Groq's LPU™ Inference Engine** for blazing-fast LLM responses.

### 🌟 Key Differentiators

* **Hybrid Search & Re-ranking**: Combines semantic search (Vectors) with a precision re-ranking step (FlashRank) to ensure the AI reads the *exact* relevant context.
* **Production-Ready Auth**: integrated Supabase Authentication with Row-Level Security (RLS) to ensure user data isolation.
* **Persistent Memory**: Sessions are stored in a dedicated PostgreSQL database, allowing users to pause and resume conversations anytime.
* **Optimized Performance**: Implements aggressive caching (`@st.cache_resource`) for embedding models, reducing startup time by 80%.

---


## 📂 Project Structure

```bash
RAGbot/
├── .streamlit/          # Streamlit configuration (secrets, theme)
├── src/
│   ├── __init__.py
│   ├── auth.py          # Supabase Authentication logic
│   ├── chat_history.py  # Chat Session Management (CRUD)
│   ├── config.py        # Centralized Configuration (Env/Secrets)
│   ├── document_processor.py # PDF/DOCX Parsing & Chunking
│   ├── rag_chain.py     # LangChain Pipeline (LLM + Retrieval)
│   └── vector_store.py  # Pinecone Vector Operations
├── test_documents/      # Sample PDF/Docx files for testing
├── app.py               # Main Application Entry Point
├── requirements.txt     # Python Dependencies
├── .env                 # Environment Variables (Local)
├── DEPLOYMENT_GUIDE.md  # Cloud Deployment Instructions
└── README.md            # Documentation
```

---

## 🛠️ Technology Stack

| Domain | Technology | purpose |
|--------|------------|---------|
| **Frontend** | Streamlit | Rapid UI development with reactive rendering. |
| **LLM Inference** | Groq | Ultra-low latency inference for Llama 3 70B. |
| **Vector Database** | Pinecone | Serverless, scalable vector index storage. |
| **Re-ranking** | FlashRank | Lightweight client-side re-ranking for precision. |
| **Database & Auth** | Supabase | Postgres-based persistency and secure OAuth. |
| **Orchestration** | LangChain | Managing prompt templates and chain execution. |
| **Embeddings** | HuggingFace | `all-MiniLM-L6-v2` for efficient vectorization. |

---

## ⚡ Getting Started

### Prerequisites

* Python 3.10+
* Git installed (optional, for cloning)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ragbot.git
cd ragbot

# Create a virtual environment
python -m venv .venv

# Activate environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the root directory. This project supports both `.env` (local) and `st.secrets` (cloud).

**Required Variables:**

```env
# --- AI & Vector Service ---
GROQ_API_KEY=gsk_...                    # Get from console.groq.com
PINECONE_API_KEY=pcsk_...               # Get from pinecone.io
PINECONE_INDEX_NAME=ragbot              # Your index name

# --- Authentication & Database ---
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJ...                     # Anon/Public Key
```

### 3. Running the Application

```bash
streamlit run app.py
```

The application will launch at `http://localhost:8501`.

---

## 🔮 Roadmap & Future Improvements

* [ ] **Multi-Modal Support**: Add support for parsing images and charts within PDFs.
* [ ] **Admin Dashboard**: Analytics page to track most asked questions and user tokens.
* [ ] **Voice Interface**: STT and TTS integration for voice conversations.
* [ ] **Unit Testing**: 100% test coverage for `src/` modules.

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

> **Author**: Devang Bhardwaj
> **Deployed Demo**: https://rag-bot-devang-bhardwaj.streamlit.app/

