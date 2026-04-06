import os
import asyncio
import numpy as np
import pandas as pd
import faiss
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from tqdm.asyncio import tqdm_asyncio

# Load environment
ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

CSV_PATH = Path(__file__).parent / "data" / "cuisines.csv"
EMB_PATH = Path(__file__).parent / "data" / "embeddings_max.npy"
CHUNKS_PATH = Path(__file__).parent / "data" / "chunks_max.txt"
INDEX_PATH = Path(__file__).parent / "data" / "faiss_max.index"

# LangChain Embedding Model
emb = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT"),
    openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_version="2024-02-15-preview",
)

# ---------------------------------------------------------
# ✅ Step 1 — Load and build chunks
# ---------------------------------------------------------
df = pd.read_csv(CSV_PATH)
df.fillna("", inplace=True)

chunks = [
    f"NAME: {row['name']}\nCUISINE: {row['cuisine']}\nCOURSE: {row['course']}\n"
    f"DESCRIPTION: {row['description']}\nINGREDIENTS: {row['ingredients']}"
    for _, row in df.iterrows()
]

print(f"✅ Loaded {len(chunks)} chunks.")

# ---------------------------------------------------------
# ✅ Step 2 — Async parallel embedding (super fast)
# ---------------------------------------------------------

# Break list into batches of 32 for maximum Azure throughput
def batch_list(lst, batch_size=32):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]

async def embed_batches():
    results = []
    batches = list(batch_list(chunks, 32))
    print(f"🚀 Sending {len(batches)} batches to Azure...")

    for batch in tqdm_asyncio(batches, desc="Embedding", total=len(batches)):
        try:
            vecs = await emb.aembed_documents(batch)
            results.extend(vecs)
        except Exception as e:
            print(f"❌ Error embedding batch: {e}")
    return results

# Run async embedding loop
embeddings = asyncio.run(embed_batches())
embeddings = np.array(embeddings, dtype="float32")

print(f"✅ Embeddings shape = {embeddings.shape}")

# ---------------------------------------------------------
# ✅ Step 3 — Save embeddings & chunks
# ---------------------------------------------------------
np.save(EMB_PATH, embeddings)
print("✅ Saved embeddings.npy")

with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
    f.write("=====CHUNK=====".join(chunks))
print("✅ Saved chunks.txt")

# ---------------------------------------------------------
# ✅ Step 4 — Build FAISS index
# ---------------------------------------------------------
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
faiss.write_index(index, str(INDEX_PATH))

print("✅ Saved faiss.index")
print("🎉 Build completed successfully!")