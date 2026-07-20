import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy
from collections import defaultdict
import mlflow

RATINGS_PATH = "data/raw/interactions/2026-07-20/ratings.csv"


def precision_recall_at_k(predictions, k=10, threshold=3.5):
    user_est_true = defaultdict(list)
    for uid, _, true_r, est, _ in predictions:
        user_est_true[uid].append((est, true_r))

    precisions = {}
    recalls = {}

    for uid, user_ratings in user_est_true.items():
        user_ratings.sort(key=lambda x: x[0], reverse=True)

        n_rel = sum((true_r >= threshold) for (_, true_r) in user_ratings)
        n_rec_k = sum((est >= threshold) for (est, _) in user_ratings[:k])
        n_rel_and_rec_k = sum(
            ((true_r >= threshold) and (est >= threshold))
            for (est, true_r) in user_ratings[:k]
        )

        precisions[uid] = n_rel_and_rec_k / n_rec_k if n_rec_k != 0 else 0
        recalls[uid] = n_rel_and_rec_k / n_rel if n_rel != 0 else 0

    avg_precision = sum(prec for prec in precisions.values()) / len(precisions)
    avg_recall = sum(rec for rec in recalls.values()) / len(recalls)
    return avg_precision, avg_recall


def main():
    print("Loading data...")
    df = pd.read_csv(RATINGS_PATH)

    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[["user_id", "item_id", "rating"]], reader)

    trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

    mlflow.set_experiment("recomart_recommender")

    with mlflow.start_run(run_name="SVD_baseline"):
        n_factors = 50
        n_epochs = 20
        lr_all = 0.005
        reg_all = 0.02

        mlflow.log_param("model", "SVD")
        mlflow.log_param("n_factors", n_factors)
        mlflow.log_param("n_epochs", n_epochs)
        mlflow.log_param("lr_all", lr_all)
        mlflow.log_param("reg_all", reg_all)

        print("Training SVD model...")
        model = SVD(n_factors=n_factors, n_epochs=n_epochs, lr_all=lr_all, reg_all=reg_all, random_state=42)
        model.fit(trainset)

        print("Evaluating...")
        predictions = model.test(testset)

        rmse = accuracy.rmse(predictions, verbose=False)
        mae = accuracy.mae(predictions, verbose=False)
        precision, recall = precision_recall_at_k(predictions, k=10, threshold=3.5)

        mlflow.log_metric("RMSE", rmse)
        mlflow.log_metric("MAE", mae)
        mlflow.log_metric("Precision_at_10", precision)
        mlflow.log_metric("Recall_at_10", recall)

        print(f"RMSE: {rmse:.4f}")
        print(f"MAE: {mae:.4f}")
        print(f"Precision@10: {precision:.4f}")
        print(f"Recall@10: {recall:.4f}")

        results_df = pd.DataFrame(predictions, columns=["user_id", "item_id", "actual", "predicted", "details"])
        results_df.drop(columns=["details"], inplace=True)
        results_df.to_csv("data/processed/sample_predictions.csv", index=False)
        mlflow.log_artifact("data/processed/sample_predictions.csv")

        print("Run logged to MLflow. Run 'mlflow ui' to view the dashboard.")


if __name__ == "__main__":
    main()