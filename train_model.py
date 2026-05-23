# UPDATED BY COPILOT: clean training script
import os
import pickle
import argparse

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from feature_extraction import extract_features


def find_and_load_dataset(cli_path=None):
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "qr.csv"),
        os.path.expanduser("~/Downloads/qr.csv"),
        r"C:\\Users\\LENOVO\\Downloads\\qr.csv",
        "qr.csv",
    ]
    if cli_path:
        possible_paths.insert(0, cli_path)

    for p in possible_paths:
        if os.path.exists(p):
            df = pd.read_csv(p)
            print(f"Dataset loaded from: {p} ({len(df)} rows)")
            return df
    return None


def main():
    parser = argparse.ArgumentParser(description="Train QR safety model")
    parser.add_argument("--data", help="Path to CSV dataset (default: search for qr.csv)")
    args = parser.parse_args()

    df = find_and_load_dataset(args.data)
    if df is None:
        raise FileNotFoundError(
            "Dataset not found. Place 'qr.csv' in the project directory or in Downloads, "
            "or run with --data /path/to/your.csv"
        )

    X = []
    y = []
    print(df["label"].value_counts())
    for index, row in df.iterrows():
        url = row['url']
        label = row['label']
        features = extract_features(url)
        X.append(features)
        y.append(label)

    X = np.array(X)
    y = np.array(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=20, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model trained! Accuracy: {accuracy * 100:.2f}%")

    pickle.dump(model, open("model.pkl", "wb"))
    print("Model saved as model.pkl")


if __name__ == "__main__":
    main()
