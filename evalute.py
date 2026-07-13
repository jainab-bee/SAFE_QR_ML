import pickle
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)

from feature_extraction import extract_features


csv_path = r"C:\Users\LENOVO\Desktop\raw_data.csv"
model_path = "model.pkl"

df = pd.read_csv(csv_path)

X = np.array([extract_features(url) for url in df["url"]])
y = df["label"].values

_, X_test, _, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)

with open(model_path, "rb") as file:
    model = pickle.load(file)

predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, predictions)
precision = precision_score(y_test, predictions, zero_division=0,pos_label="phishing",)
recall = recall_score(y_test, predictions, zero_division=0,pos_label="phishing",)
f1 = f1_score(y_test, predictions, zero_division=0,pos_label="phishing",)
roc_auc = roc_auc_score(y_test, probabilities)

report = classification_report(y_test, predictions,labels=["legitimate", "phishing"],zero_division=0)
matrix = confusion_matrix(y_test, predictions,labels=["legitimate", "phishing"])

with open("evaluation_report.txt", "w") as file:
    file.write(f"Accuracy: {accuracy:.4f}\n")
    file.write(f"Precision: {precision:.4f}\n")
    file.write(f"Recall: {recall:.4f}\n")
    file.write(f"F1 Score: {f1:.4f}\n")
    file.write(f"ROC AUC: {roc_auc:.4f}\n\n")
    file.write("Classification Report:\n")
    file.write(report)
    file.write("\nConfusion Matrix:\n")
    file.write(str(matrix))

print("Evaluation completed")
print("Saved evaluation_report.txt")
