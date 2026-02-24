import os
import time
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
            messages=[{"role": "user", "content": f"""You are a quiz generator for OpenGradient. Generate 10 multiple choice questions.

Random seed: {os.urandom(8).hex()}
Timestamp: {int(time.time())}
Random topic offset: {int.from_bytes(os.urandom(2), 'big') % 100}
Pick a completely different set of topics this time. Do not use the same questions as before.

STRICT RULES:
- Every quiz MUST be completely different. Never repeat the same questions.
- Randomly pick from these specific topics and rotate them differently each time:
  * OpenGradient's mission and vision
  * How TEE (Trusted Execution Environment) works in OpenGradient
  * zkML proofs and how they work
  * The OG token utility and economics
  * Model Hub features and how to use it
  * MemSync and AI memory
  * Digital Twins on twin.fun
  * BitQuant and AI trading
  * x402 protocol and trustless inference
  * Base Sepolia testnet integration
  * OpenGradient SDK features
  * Verifiable AI inference explained
  * OpenGradient network architecture
  * Decentralized AI compute
  * On-chain AI agents
  * OpenGradient backers (a16z, Coinbase etc)
  * Real world use cases of OpenGradient
  * How to run inference on OpenGradient
  * OpenGradient vs centralized AI
  * EVM compatibility in OpenGradient

- Make the correct answer position RANDOM — spread answers across index 0, 1, 2, 3 evenly
- Questions should be interesting and educational, not too hard
- Make wrong options plausible but clearly wrong to someone who knows OpenGradient

Return ONLY a JSON array like this:
[
  {{
    "question": "question here",
    "options": ["option A", "option B", "option C", "option D"],
    "answer": 2
  }}
]
answer is the index (0-3) of the correct option."""}],
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
