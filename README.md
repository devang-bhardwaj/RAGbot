# RAGbot 🤖

AI-Powered Document Q&A Chatbot - Upload documents and ask questions about them!

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-121212?style=for-the-badge)

## ✨ Features

- 📄 **Document Upload** - Support for PDF, DOCX, and TXT files
- 🔍 **Semantic Search** - Find relevant information using AI embeddings
- 💬 **Chat Interface** - Natural conversation about your documents
- 🔐 **User Authentication** - Secure login with Supabase
- 🆓 **100% Free** - Using Groq, ChromaDB, and Streamlit Cloud

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+** installed
2. **Groq API Key** (free) - Get it at [console.groq.com](https://console.groq.com)
3. **Supabase Project** (free) - Create at [supabase.com](https://supabase.com)

### Local Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/RAGbot.git
cd RAGbot

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env with your API keys
# GROQ_API_KEY=your_key_here
# SUPABASE_URL=your_url_here
# SUPABASE_KEY=your_key_here

# Run the app
streamlit run app.py
```

### Setting up Supabase

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Go to **Settings > API**
3. Copy the **Project URL** → `SUPABASE_URL`
4. Copy the **anon public** key → `SUPABASE_KEY`
5. Go to **Authentication > Settings**
6. Under "Email Auth", ensure email confirmations are enabled (or disable for testing)

## 🌐 Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set your secrets in **App Settings > Secrets**:

```toml
GROQ_API_KEY = "your_groq_api_key"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your_supabase_anon_key"
```

1. Click Deploy!

## 📁 Project Structure

```
RAGbot/
├── .streamlit/
│   └── config.toml      # Theme configuration
├── src/
│   ├── auth.py          # Supabase authentication
│   ├── config.py        # App configuration
│   ├── document_processor.py  # PDF, DOCX, TXT parsing
│   ├── rag_chain.py     # Groq LLM integration
│   └── vector_store.py  # ChromaDB operations
├── app.py               # Main Streamlit app
├── requirements.txt     # Python dependencies
└── .env.example         # Environment template
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| LLM | Groq (Llama 3.3 70B) |
| Vector DB | ChromaDB |
| Embeddings | Sentence Transformers |
| Auth | Supabase |
| Hosting | Streamlit Cloud |

## 📝 Usage

1. **Sign Up/Login** - Create an account or sign in
2. **Upload Documents** - Use the sidebar to upload PDF, DOCX, or TXT files
3. **Ask Questions** - Type your questions in the chat
4. **Get AI Answers** - Receive responses based on your documents

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit PRs.

## 📄 License

MIT License - feel free to use this project for learning or commercial purposes.

---

Built with ❤️ using Streamlit & Groq
