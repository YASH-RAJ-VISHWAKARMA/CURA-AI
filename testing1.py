import numpy as np
import pandas as pd
import tensorflow as tf
import joblib

# -------------------------
# 1. Load model & encoder
# -------------------------
model = tf.keras.models.load_model("disease_model.h5")
label_encoder = joblib.load("label_encoder.pkl")

# Load training dataset again (to get symptom columns)
train_data = pd.read_csv(r"C:\yash\coding\python\college\disease prediction model\archive\Training_disease_prediction.csv")
symptom_columns = train_data.drop("prognosis", axis=1).columns

# -------------------------
# 2. Function: Predict Disease
# -------------------------
def predict_disease(user_symptoms):
    input_data = np.zeros(len(symptom_columns))

    for symptom in user_symptoms:
        if symptom in symptom_columns:
            input_data[symptom_columns.get_loc(symptom)] = 1
        else:
            print(f"⚠️ Warning: Symptom '{symptom}' not in dataset!")

    prediction = model.predict(input_data.reshape(1, -1))
    predicted_disease = label_encoder.inverse_transform([np.argmax(prediction)])
    return predicted_disease[0]

# -------------------------
# 3. Example Usage
# -------------------------
if __name__ == "__main__":
    user_input = ["itching", "skin_rash", "joint_pain"]
    disease = predict_disease(user_input)
    print("Predicted Disease:", disease)
