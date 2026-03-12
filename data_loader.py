import pandas as pd
import json

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_all_data():
    return {
        "df_clustered": pd.read_csv("data/df_clustered.csv"),
        "career_islands": load_json("data/career_islands.json"),
        "cluster_to_islands": load_json("data/cluster_to_islands.json"),
        "interest_to_islands": load_json("data/interest_to_islands.json"),
        "interest_keywords": load_json("data/interest_keywords.json"),
        "interest_island_weights": load_json("data/interest_island_weights.json"),
        "profession_to_topics": load_json("data/profession_to_topics.json"),
        "index_to_islands": load_json("data/index_to_islands.json"),
    }
