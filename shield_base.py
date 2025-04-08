from transformers import AutoModelForSequenceClassification, AutoTokenizer
import pandas as pd
import torch

# Load the pre-trained model and tokenizer
print("Loading DistilBERT model for phishing detection...")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

# Mock data (we'll replace this with real data later)
print("Loading mock data...")
data = pd.DataFrame({
    "url": ["http://fakebank.com/login", "https://google.com", "http://scam123.com"],
    "label": [1, 0, 1]  # 1 = phishing, 0 = safe
})

# Tokenize the URLs
print("Tokenizing URLs...")
inputs = tokenizer(data["url"].tolist(), padding=True, truncation=True, return_tensors="pt")

# Run the model
print("Running model inference...")
with torch.no_grad():
    outputs = model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=1)

# Add predictions to the data
data["prediction"] = predictions.numpy()
data["prediction_label"] = data["prediction"].map({1: "Phishing", 0: "Safe"})

# Print results
print("\nResults:")
print(data[["url", "prediction_label"]])

# Save results to a file
data.to_csv("shield_results.csv", index=False)
# print("Results saved to shield_results.csv")

import subprocess

# Clone a Git repository
subprocess.run(["git", "clone", "https://github.com/shieldaigent/shieldbase.git"])


