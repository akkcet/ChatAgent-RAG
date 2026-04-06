import os
import numpy as np
import pandas as pd
import faiss
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

CSV_PATH = Path(__file__).parent / "data" / "cuisines.csv"
INDEX_PATH = Path(__file__).parent / "data" / "faiss.index"
EMB_PATH = Path(__file__).parent / "data" / "embeddings.npy"
CHUNKS_PATH = Path(__file__).parent / "data" / "chunks.txt"

df = pd.read_csv(CSV_PATH)
df.fillna("", inplace=True)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

print("Building chunks...")
chunks = [
    "NAME: {}\nCUISINE: {}\nCOURSE: {}\nDESCRIPTION: {}\nINGREDIENTS: {}".format(
        row["name"], row["cuisine"], row["course"], row["description"], row["ingredients"]
    )
    for _, row in df.iterrows()
]

print("Embedding {} chunks...".format(len(chunks)))
embeddings = []
for chunk in chunks:
    e = client.embeddings.create(
        input=chunk,
        model=os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT")
    )
    embeddings.append(e.data[0].embedding)

embeddings = np.array(embeddings, dtype="float32")

np.save(EMB_PATH, embeddings)
print("Saved embeddings.")

with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
    f.write("=====CHUNK=====".join(chunks))
print("Saved chunks.")

print("Building FAISS index...")
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
faiss.write_index(index, str(INDEX_PATH))
print("✅ Index build complete!")