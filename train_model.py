import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from feature_extraction import extract_features

df = pd.read_csv("C:\\Users\\LENOVO\\Downloads\\qr.csv")
print(f"Loaded data: {len(df)} rows")

X = np.array([extract_features(url) for url in df["url"]])
y = df["label"].to_numpy()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=50, random_state=42)
model.fit(X_train, y_train)

accuracy = accuracy_score(y_test, model.predict(X_test))
print(f"Accuracy: {accuracy*100:.2f}%")

pickle.dump(model, open("model.pkl", "wb"))
print("Model saved as model.pkl")



