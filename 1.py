import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow import keras
import joblib
import os

# -------------------------
# 1. Load Train & Test Datasets
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
archive_dir = os.path.join(BASE_DIR, "archive")

print(BASE_DIR)
print(archive_dir)

train_path = os.path.join(archive_dir, "Training_disease_prediction.csv")
test_path = os.path.join(archive_dir, "Testing_disease_prediction.csv")

train_data = pd.read_csv(train_path)
test_data = pd.read_csv(test_path)

# -------------------------
# 2. Clean and Align Data
# -------------------------
# Drop the unwanted column if it exists
if "Unnamed: 133" in train_data.columns:
    train_data = train_data.drop("Unnamed: 133", axis=1)

# Separate features & target
X_train = train_data.drop("prognosis", axis=1)
y_train = train_data["prognosis"]

X_test = test_data.drop("prognosis", axis=1)
y_test = test_data["prognosis"]

# Align test columns with train columns
X_test = X_test.reindex(columns=X_train.columns, fill_value=0)

# -------------------------
# 3. Encode Labels
# -------------------------
label_encoder = LabelEncoder()
y_train = label_encoder.fit_transform(y_train)
y_test = label_encoder.transform(y_test)

# -------------------------
# 4. Convert to NumPy Arrays
# -------------------------
X_train = X_train.to_numpy(dtype=np.float32)
X_test = X_test.to_numpy(dtype=np.float32)
y_train = np.array(y_train, dtype=np.int64)
y_test = np.array(y_test, dtype=np.int64)

print("Train shape:", X_train.shape, " Test shape:", X_test.shape)
print("Unique diseases:", len(label_encoder.classes_))

# -------------------------
# 5. Build Deep Learning Model
# -------------------------
model = keras.Sequential([
    keras.layers.Dense(256, activation="relu", input_shape=(X_train.shape[1],)),
    keras.layers.Dropout(0.4),
    keras.layers.Dense(128, activation="relu"),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(len(np.unique(y_train)), activation="softmax")
])

model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

# -------------------------
# 6. Train Model
# -------------------------
history = model.fit(
    X_train, y_train,
    epochs=50,
    batch_size=32,
    validation_data=(X_test, y_test)
)

# -------------------------
# 7. Evaluate Model
# -------------------------
loss, acc = model.evaluate(X_test, y_test)
print(f"✅ Test Accuracy: {acc*100:.2f}%")

# -------------------------
# 8. Test Prediction
# -------------------------
sample_input = np.array([X_test[0]])
prediction = model.predict(sample_input)
predicted_disease = label_encoder.inverse_transform([np.argmax(prediction)])

print("Predicted Disease:", predicted_disease[0])
print("Actual Disease:", label_encoder.inverse_transform([y_test[0]]))

# -------------------------
# 9. Save Model & Encoder
# -------------------------

MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "disease_model.h5")
ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")

model.save(MODEL_PATH)
joblib.dump(label_encoder, ENCODER_PATH)

print(f"💾 Model saved at {MODEL_PATH}")
print(f"💾 Encoder saved at {ENCODER_PATH}")

