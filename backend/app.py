import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)   
CORS(app)              
from transformers import pipeline
import datetime

# ----------------------------
# APP SETUP
# ----------------------------
app = Flask(__name__)
CORS(app)

# ----------------------------
# AI MODEL
# ----------------------------
chatbot = pipeline(
    "text-generation",
    model="google/flan-t5-small"
)

# ----------------------------
# HARMFUL KEYWORDS LIST
# ----------------------------
harmful_keywords = [
    "bomb",
    "make a bomb",
    "explosive",
    "kill",
    "murder",
    "terrorist",
    "weapon",
    "suicide",
    "poison",
    "hack",
    "illegal",
    "attack",
    "mass killing",
    "chemical weapon",
    "biological weapon"
]

# ----------------------------
# RISK ANALYSIS FUNCTION
# ----------------------------
def analyze_risk(text):
    text = text.lower()
    matched = []

    for word in harmful_keywords:
        if word in text:
            matched.append(word)

    score = len(matched)

    if score == 0:
        return {
            "risk_level": "LOW",
            "blocked": False,
            "matched_keywords": []
        }

    elif score <= 2:
        return {
            "risk_level": "MEDIUM",
            "blocked": True,
            "matched_keywords": matched
        }

    else:
        return {
            "risk_level": "HIGH",
            "blocked": True,
            "matched_keywords": matched
        }

# ----------------------------
# SAFE RESPONSE
# ----------------------------
def safe_response():
    return "⚠️ I cannot provide harmful, illegal, or dangerous instructions."

# ----------------------------
# LOGGING
# ----------------------------
def log_event(user_input, risk):
    with open("security_logs.txt", "a") as f:
        f.write("\n----------------------\n")
        f.write(str(datetime.datetime.now()) + "\n")
        f.write("INPUT: " + user_input + "\n")
        f.write("RISK: " + str(risk) + "\n")

# ----------------------------
# CHAT ENDPOINT
# ----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    # Step 1: Risk check
    risk = analyze_risk(user_message)

    # Step 2: Block if unsafe
    if risk["blocked"]:
        log_event(user_message, risk)
        return jsonify({
            "response": safe_response(),
            "risk_analysis": risk
        })

    # Step 3: Safe AI response
    try:
       result = chatbot(user_message)
       return jsonify({"response": result[0]["generated_text"]})

    except Exception as e:
        return jsonify({"error": str(e)})

# ----------------------------
# HOME ROUTE
# ----------------------------
@app.route("/")
def home():
    return "IronGuard Chat is running"

# ----------------------------
# RUN SERVER
# ----------------------------
if __name__ == "__main__":
    app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 5000))
)