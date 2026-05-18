from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)   
CORS(app)              
from transformers import pipeline
import datetime

app = Flask(__name__)
CORS(app)

chatbot = pipeline(
    "text-generation",
    model="google/flan-t5-small"
)

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

def safe_response():
    return "⚠️ I cannot provide harmful, illegal, or dangerous instructions."

def log_event(user_input, risk):
    with open("security_logs.txt", "a") as f:
        f.write("\n----------------------\n")
        f.write(str(datetime.datetime.now()) + "\n")
        f.write("INPUT: " + user_input + "\n")
        f.write("RISK: " + str(risk) + "\n")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    risk = analyze_risk(user_message)

    if risk["blocked"]:
        log_event(user_message, risk)
        return jsonify({
            "response": safe_response(),
            "risk_analysis": risk
        })

    try:
       result = chatbot(user_message)
       return jsonify({"response": result[0]["generated_text"]})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/")
def home():
    return "IronGuard Chat is running"

if __name__ == "__main__":
    port = 5001
    app.run(host="0.0.0.0", port=port)