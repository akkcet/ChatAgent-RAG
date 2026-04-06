import pandas as pd
from pathlib import Path

class ProductEngine:
    def __init__(self):
        csv = Path(__file__).parent / "data" / "cuisines.csv"
        self.df = pd.read_csv(csv)
        self.df.fillna("", inplace=True)

    def search_products(self, q):
        res = self.df[self.df["name"].str.contains(q, case=False)]
        if res.empty:
            return "No dishes found."
        return list(res["name"])

    def get_ingredients(self, dish):
        row = self.df[self.df["name"].str.lower() == dish.lower()]
        if row.empty:
            return None
        return row["ingredients"].iloc[0]