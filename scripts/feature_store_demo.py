import json
import pandas as pd

# Load the feature registry (metadata about available features)
with open("feature_store/feature_registry.json") as f:
    registry = json.load(f)

print(f"Feature store version: {registry['feature_store_version']}")
print(f"Available features:")
for feat in registry["features"]:
    print(f" - {feat['name']} (entity: {feat['entity']}, type: {feat['dtype']})")

# Simulate retrieval: fetch features for a specific user (e.g. training/inference lookup)
feature_table = pd.read_csv("data/processed/feature_table.csv")

def get_user_features(user_id):
    row = feature_table[feature_table["user_id"] == user_id].iloc[0]
    return {
        "user_id": user_id,
        "user_activity_count": row["user_activity_count"],
        "user_avg_rating": row["user_avg_rating"],
        "age_normalized": row["age_normalized"],
        "occupation_encoded": row["occupation_encoded"],
    }

def get_item_features(item_id):
    row = feature_table[feature_table["item_id"] == item_id].iloc[0]
    return {
        "item_id": item_id,
        "item_popularity": row["item_popularity"],
        "item_avg_rating": row["item_avg_rating"],
    }

# Demo retrieval
print("\n--- Sample retrieval for user_id=1 ---")
print(get_user_features(1))

print("\n--- Sample retrieval for item_id=1 ---")
print(get_item_features(1))