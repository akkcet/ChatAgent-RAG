from collections import defaultdict
import pandas as pd
from pathlib import Path

class Recommender:
    def __init__(self):
        csv = Path(__file__).parent / "data" / "cuisines.csv"
        self.df = pd.read_csv(csv)
        self.df.fillna("", inplace=True)
        self.history = defaultdict(list)

    def recommend(self, user, _msg=None):
        if len(self.history[user]) == 0:
            return "Ask about a dish first."

        last = self.history[user][-1]
        row = self.df[self.df["name"] == last]

        if row.empty:
            return "No recommendations."

        cuisine = row["cuisine"].iloc[0]
        candidates = self.df[self.df["cuisine"] == cuisine]["name"].tolist()
        candidates = [c for c in candidates if c != last]

        if not candidates:
            return "No similar dishes found."
        return candidates[0]