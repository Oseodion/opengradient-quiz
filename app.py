import os
import json
import random
import time
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)

client = None

def get_client():
    global client
    if client is None:
        import opengradient as og
        os.environ["BASE_SEPOLIA_RPC_URL"] = os.getenv("BASE_SEPOLIA_RPC_URL", "")
        client = og.init(private_key=os.getenv("PRIVATE_KEY", ""))
        client.llm.ensure_opg_approval(opg_amount=5)
    return client

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
        import opengradient as og
        c = get_client()

        all_topics = [
            "How TEE (Trusted Execution Environment) ensures secure AI inference",
            "What zkML proofs are and how OpenGradient uses them",
            "The OG token — what it's used for and how to earn it",
            "OpenGradient Model Hub — how to host and explore AI models",
            "MemSync — how it handles AI memory across apps",
            "Digital Twins on twin.fun — what they are and how they work",
            "BitQuant — AI-powered quantitative trading analysis",
            "x402 protocol — trustless and verifiable AI inference",
            "Base Sepolia testnet — why OpenGradient uses it",
            "OpenGradient SDK — how developers build on-chain AI apps",
            "Verifiable AI — why it matters and how OpenGradient achieves it",
            "OpenGradient network architecture — nodes, compute, and consensus",
            "Decentralized AI compute — how OpenGradient distributes workloads",
            "On-chain AI agents — what they are and real use cases",
            "OpenGradient backers — a16z, Coinbase, and other investors",
            "Real world use cases of verifiable AI in Web3",
            "How to run inference on OpenGradient network",
            "OpenGradient vs centralized AI providers like OpenAI",
            "EVM compatibility — how OpenGradient works with Ethereum",
            "OpenGradient's mission — open and verifiable AI for everyone",
            "How privacy is preserved during AI inference in OpenGradient",
            "What makes OpenGradient different from other AI blockchains",
            "How developers deploy AI models on OpenGradient",
            "OpenGradient's approach to AI transparency and auditability",
        ]

        selected_topics = random.sample(all_topics, 10)
        seed = os.urandom(8).hex()
        timestamp = int(time.time())

        prompt = f"""You are a quiz generator. Generate exactly 10 multiple choice questions about OpenGradient.

Timestamp: {timestamp}
Seed: {seed}

You MUST generate one question per topic below. Use EXACTLY these 10 topics in this order:
{chr(10).join(f"{i+1}. {t}" for i, t in enumerate(selected_topics))}

RULES:
- Each question must be specifically about that topic
- Make 4 answer options per question
- Spread correct answer positions: use index 0, 1, 2, 3 randomly — NOT always 0
- Keep questions educational and not too hard

Return ONLY a JSON array, no markdown, no explanation:
[
  {{
    "question": "question text",
    "options": ["option A", "option B", "option C", "option D"],
    "answer": 2
  }}
]"""

        response = c.llm.chat(
            model=og.TEE_LLM.GPT_4O,
            messages=[{"role": "user", "content": prompt}],
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
