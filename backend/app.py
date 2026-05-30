from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import datetime

app = Flask(__name__)
CORS(app)

MODEL_NAME = "distilgpt2"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

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

    elif score <= 2:
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
                "error": "No JSON body received"
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

        prompt = f"User: {user_message}\nAssistant:"

        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=128
        )

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=50,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id
            )

        generated_text = tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

        if "Assistant:" in generated_text:
            response = generated_text.split("Assistant:", 1)[1].strip()
        else:
            response = generated_text.strip()

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
        port=8080,
        debug=False
    )
