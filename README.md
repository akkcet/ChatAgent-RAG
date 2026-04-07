#  Smart Recipe Assistant (RAG + Azure OpenAI + Streamlit)

A fully‑featured **AI recipe assistant** powered by:

✅ Azure OpenAI (GPT‑4o + Embeddings)  
✅ RAG (FAISS Vector Search)  
✅ Ingredient extraction  
✅ Ingredient ordering workflow  
✅ Persistent order history  
✅ Personalized recommendations  
✅ Streamlit UI  
✅ Multi‑tool agent architecture  

---

##  **Project Structure**

```
retail-chatbot-rag/
│
├── backend/
│   ├── chat_ui.py              #  Streamlit UI entry point
│   ├── chat_agent.py           # Multi-tool AI agent
│   ├── rag_index.py            # FAISS RAG loader
│   ├── index_max.py            # Build FAISS + embeddings (better performance)
│   ├── product_engine.py       # Dish search
│   ├── recommender.py          # Simple dish recommender 
│   ├── order_manager.py        # Order storage
│   ├── tools.py                # Tool wrapper
│   └── data/
│       ├── cuisines.csv        # Source data
│       ├── embeddings.npy      # Built via build_index.py
│       ├── faiss.index         # FAISS index
│       └── orders.json         # Auto‑generated order history
│
├── requirements.txt
└── README.md
```

---

##  Features

### ✅ **1. RAG‑powered recipe search**
Uses FAISS + Azure embeddings to search recipes semantically.

### ✅ **2. Strict grounded answering**
All recipe answers come ONLY from your CSV (no hallucinations).

### ✅ **3. Ingredient extraction**
Supports:
- Bullet lists  
- Measurements  
- Multi‑line ingredients  
- Section‑based extraction  

### ✅ **4. Ingredient ordering workflow**
Bot asks:
> “Would you like me to order ALL these ingredients?”

Accepts:
- “yes”, “sure”, “ok”, “order now”
- “no”, “nope”, “no thanks”

### ✅ **5. Persistent order history**
Saved to:
```
backend/data/orders.json
```

### ✅ **6. Personalized welcome-back recommendations**
When user returns and says **hi/hello/hey**, bot shows:
- recommendations based on past orders

### ✅ **7. Clean Streamlit UI**
- Chat bubbles  
- Typing animation  
- Sidebar order history  
- Ingredient highlight boxes  

---

##  Setup Instructions (Local Development)

### ✅ 1. Create a virtual environment
```bash
python -m venv my-env
my-env\Scripts\activate
```

### ✅ 2. Install dependencies
```bash
pip install -r requirements.txt
```

### ✅ 3. Create `.env` file in project root
```
AZURE_OPENAI_KEY=YOUR_KEY
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt4o
AZURE_OPENAI_EMBED_DEPLOYMENT=myembed
```

### ✅ 4. Build the FAISS index (run once)
```bash
python backend/build_index.py
```

This generates:
- `data/faiss.index`
- `data/embeddings.npy`
- `data/chunks.txt`

### ✅ 5. Run Streamlit app
```bash
streamlit run backend/streamlit_app.py
```

Your app will open at:
```
http://localhost:8501
```

---

##  Deploying to Streamlit Cloud

### ✅ 1. Push your repo to GitHub
Required files:
- `backend/streamlit_app.py`
- Everything inside `backend/`
- `requirements.txt`

Do **NOT** push `.env`.

### ✅ 2. Go to Streamlit Cloud
 https://share.streamlit.io

### ✅ 3. New App → Select your GitHub repo

### ✅ 4. Set **Main file path** to:
```
backend/streamlit_app.py
```

### ✅ 5. Add secrets in Streamlit Cloud
Go to:
**App → Settings → Secrets**

Paste:
```toml
AZURE_OPENAI_KEY="YOUR_KEY"
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_CHAT_DEPLOYMENT="gpt4o"
AZURE_OPENAI_EMBED_DEPLOYMENT="myembed"
```

### ✅ 6. Deploy 

---

##  Testing the Agent
Try queries like:
```
What are the ingredients for Goan Chana Ros?
Chettinad Kuzhambu Recipe
Suggest spicy South Indian breakfast
Order my last ingredients
```

Confirm:
✅ RAG results  
✅ Ingredient extraction  
✅ Bot asks “Would you like me to order?”  
✅ “yes/no” working  
✅ Orders appear in sidebar  
✅ Welcome‑back recommendations appear only on greetings  

---

##  Troubleshooting

### ✅ “orders.json not found”
It will be auto‑created.

### ✅ “FAISS dimension mismatch”
Delete `embeddings.npy` and `faiss.index`, then rerun build:
```
python backend/build_index.py
```

### ✅ Azure 404 errors
Deployment name mismatch — verify:
- `AZURE_OPENAI_CHAT_DEPLOYMENT`
- `AZURE_OPENAI_EMBED_DEPLOYMENT`

### ✅ “I don’t know based on the available data”
Grounding basically worked but chunk didn’t contain answer.

---

