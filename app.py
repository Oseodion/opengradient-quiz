import os

import json
import opengradient as og
from flask import Flask, jsonify, send_from_directory

client = og.init(private_key=os.getenv("PRIVATE_KEY", ""))
client.llm.ensure_opg_approval(opg_amount=5)

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def styles():
    return send_from_directory('.', 'style.css')

@app.route('/logo.png')
def logo():
    return send_from_directory('.', 'logo.png')

@app.route('/generate-questions', methods=['POST'])
def generate_questions():
    try:
        response = client.llm.chat(
            model=og.TEE_LLM.GPT_4O,
            messages=[{"role": "user", "content": f"""Generate 10 multiple choice questions about OpenGradient. 
Use a random seed: {os.urandom(4).hex()}

IMPORTANT RULES:
- Make every quiz completely different from previous ones
- Randomly vary which option (A, B, C or D) is the correct answer — do NOT always make the correct answer option A
- Mix easy and medium difficulty questions
- Shuffle the correct answer position randomly across all questions

Topics to randomly pick from: what OpenGradient is, verifiable AI, TEE execution, decentralized inference, OG token, Model Hub, MemSync, Digital Twins, zkML, on-chain AI, Base Sepolia, OpenGradient SDK, BitQuant, x402 protocol, OpenGradient network architecture.

Return ONLY a JSON array, no other text, like this:
[
  {{
    "question": "What is OpenGradient?",
    "options": ["A crypto exchange", "A decentralized AI network", "A wallet", "A game"],
    "answer": 1
  }}
]
answer is the index (0,1,2,3) of the correct option. Vary the answer index across questions."""}],
            max_tokens=2500
        )

        text = response.chat_output
        if isinstance(text, dict):
            text = text.get('content', str(text))
        text = text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        questions = json.loads(text)
        return jsonify({"questions": questions})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')