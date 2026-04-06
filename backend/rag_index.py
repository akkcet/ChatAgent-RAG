import os
import numpy as np
import faiss
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI

class RAGIndex:
    def __init__(self):
        ROOT = Path(__file__).parent.parent
        load_dotenv(ROOT / ".env")
        data_dir = Path(__file__).parent / "data"

        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

        self.embeddings = np.load(data_dir / "embeddings_max.npy")
        self.index = faiss.read_index(str(data_dir / "faiss_max.index"))

        with open(data_dir / "chunks_max.txt", "r", encoding="utf-8") as f:
            self.chunks = f.read().split("=====CHUNK=====")

    def search(self, query, top_k=5):
        print("\n=== Performing RAG SEARCH ===")
        print("Query:", query)

        # embed query
        vec = self.client.embeddings.create(
            input=query,
            model=os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT")
        ).data[0].embedding

        q = np.array(vec, dtype="float32").reshape(1, -1)

        # FAISS retrieval
        distances, indices = self.index.search(q, top_k)

        # ✅ retrieve chunks
        retrieved_chunks = [self.chunks[i] for i in indices[0]]

        # ✅ print them for debugging
        print("\n--- RAG RESULTS ---")
        for i, chunk in enumerate(retrieved_chunks, start=1):
            print(f"\n🔹 Result {i}:\n{chunk[:300]}...")

        return retrieved_chunks