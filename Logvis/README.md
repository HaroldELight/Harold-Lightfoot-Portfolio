
# 🧠 Logvis – Personal AI Companion

Logvis is a **personal AI companion** that starts small but grows with you.
It’s lightweight enough to run on an **i3 laptop** while still designed to scale into a full **AI assistant** with memory, voice, and tools.

---

## 🚀 Features (Current – v1)

* Terminal-based chatbot (`main.py`)
* Short-term memory via **SQLite**
* OpenAI API integration (scalable SaaS “brain”)
* Modular structure for adding new skills

---

## 🛠️ Roadmap

### **V1 – Foundation (MVP)** ✅

* Terminal chatbot
* SQLite memory
* OpenAI API as brain

### **V2 – Personality & Tools**

* Long-term memory with **Chroma/FAISS**
* Skills: search, weather, calendar
* Settings (`settings.json`) for preferences

### **V3 – Voice & Interaction**

* Speech-to-text + text-to-speech
* Streamlit web UI
* Offline fallback (Ollama / GPT4All)

### **V4 – Smarter Memory**

* Contextual recall from past chats
* Personality traits & growth
* Daily journaling / summaries

### **V5 – Autonomy & Agents**

* Multi-step task execution
* File & email handling
* Cloud backup for memory

### **V6 – Full Companion**

* Multi-modal (text, voice, vision)
* Deploy on VPS for 24/7 access
* Custom voice cloning
* IoT / smart home integration

---

## 📂 Project Structure

```
Logvis/
│── main.py             # Entry point (chat loop or UI)
│── config.py           # API keys + settings
│── memory/             
│   └── memory.py       # SQLite/JSON memory manager
│── skills/             
│   ├── search.py       # Example tool
│   ├── weather.py      
│   └── ...
│── ai/
│   └── brain.py        # Wrapper for OpenAI API (or local Ollama)
│── data/
│   └── memory.db       # SQLite database (auto-created)
└── requirements.txt
```

---

## ⚡ Installation

```bash
git clone https://github.com/yourusername/Logvis.git
cd Logvis
pip install -r requirements.txt
```

Add your API key in `config.py`:

```python
OPENAI_API_KEY = "your-api-key-here"
```

Run Logvis:

```bash
python main.py
```

---

## 🎯 Vision

Logvis isn’t just a chatbot — it’s a **companion that evolves with you**.
Start with a simple terminal AI, then gradually add memory, tools, voice, and autonomy.

---
