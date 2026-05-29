from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import datetime

app = Flask(__name__)
CORS(app)

MODEL_NAME = "sshleifer/tiny-t5"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

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

    matched = [
        keyword
        for keyword in harmful_keywords
        if keyword in text
    ]

    score = len(matched)

    if score == 0:
        return {
            "risk_level": "LOW",
            "blocked": False,
            "matched_keywords": []
        }

    if score <= 2:
        return {
            "risk_level": "MEDIUM",
            "blocked": True,
            "matched_keywords": matched
        }

    return {
        "risk_level": "HIGH",
        "blocked": True,
        "matched_keywords": matched
    }


def safe_response():
    return "⚠️ I cannot provide harmful, illegal, or dangerous instructions."


def log_event(user_input, risk):
    with open("security_logs.txt", "a", encoding="utf-8") as f:
        f.write("\n----------------------\n")
        f.write(f"{datetime.datetime.now()}\n")
        f.write(f"INPUT: {user_input}\n")
        f.write(f"RISK: {risk}\n")


@app.route("/")
def home():
    return "IronGuard Chat is running"


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No JSON data received"
            }), 400

        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({
                "error": "Message cannot be empty"
            }), 400

        risk = analyze_risk(user_message)

        if risk["blocked"]:
            log_event(user_message, risk)

            return jsonify({
                "response": safe_response(),
                "risk_analysis": risk
            })

        inputs = tokenizer(
            user_message,
            return_tensors="pt",
            truncation=True,
            max_length=128
        )

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=50,
                do_sample=False
            )

        response = tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

        return jsonify({
            "response": response,
            "risk_analysis": risk
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=False
    )