from flask import Flask, jsonify, request
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import datetime
import logging
import torch

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

logging.basicConfig(level=logging.INFO)

MODEL_NAME = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
model.eval()

HARMFUL_KEYWORDS = [
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
    "biological weapon",
]


def analyze_risk(text):
    lowered_text = text.lower()

    matched = [
        keyword
        for keyword in HARMFUL_KEYWORDS
        if keyword in lowered_text
    ]

    if not matched:
        return {
            "risk_level": "LOW",
            "blocked": False,
            "matched_keywords": [],
        }

    if len(matched) <= 2:
        return {
            "risk_level": "MEDIUM",
            "blocked": True,
            "matched_keywords": matched,
        }

    return {
        "risk_level": "HIGH",
        "blocked": True,
        "matched_keywords": matched,
    }


def safe_response():
    return "I cannot provide harmful, illegal, or dangerous instructions."


def log_event(user_input, risk):
    with open("security_logs.txt", "a", encoding="utf-8") as file:
        file.write("\n----------------------\n")
        file.write(f"{datetime.datetime.now().isoformat()}\n")
        file.write(f"INPUT: {user_input}\n")
        file.write(f"RISK: {risk}\n")


def generate_response(user_message):
    prompt = (
        "Answer the following question clearly and helpfully. "
        "If it is a greeting, respond naturally.\n\n"
        f"Question: {user_message}\n"
        "Answer:"
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512,
    )

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=120,
            do_sample=False,
            num_beams=4,
            repetition_penalty=1.2,
            early_stopping=True,
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    if not response:
        return "Sorry, I could not generate a clear response. Please try again."

    return response


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "IronGuard Chat API is running"})


@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "No JSON body received"}), 400

        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        risk = analyze_risk(user_message)

        if risk["blocked"]:
            log_event(user_message, risk)

            return jsonify({
                "response": safe_response(),
                "risk_analysis": risk,
            }), 200

        response = generate_response(user_message)

        return jsonify({
            "response": response,
            "risk_analysis": risk,
        }), 200

    except Exception as error:
        app.logger.exception("Chat endpoint failed")
        return jsonify({"error": str(error)}), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8080,
        debug=False,
        use_reloader=False,
        threaded=False,
    )