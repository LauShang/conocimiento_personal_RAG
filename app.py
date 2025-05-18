import os
import logging
import time
from src.utils import setup_logging, Config
from flask import Flask, render_template, request, jsonify
from src.model_cp import PersonalKnowleged
# Configuración de logging
logger = logging.getLogger(__name__)
setup_logging(debug_mode=True,file='logs/rag.log')
# Configuración de la aplicación
config = Config()
# variables de entorno
os.environ["LANGSMITH_TRACING"] = config.creds.get("LANGSMITH_TRACING")
os.environ["LANGSMITH_ENDPOINT"] = config.creds.get("LANGSMITH_ENDPOINT")
os.environ["LANGSMITH_API_KEY"] = config.creds.get("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = config.creds.get("LANGSMITH_PROJECT")
model = PersonalKnowleged(config=config)

app = Flask(__name__)

@app.route('/')
def chat():
    return render_template('chat.html')

@app.route('/input')
def input_data():
    return render_template('input.html')

@app.route('/process', methods=['POST'])
def process():
    time.sleep(5)  # Simulate processing time
    return jsonify({"message": "Successful"})

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get('question')
    if not question:
        return jsonify({"error": "No question provided"}), 400

    answer = model.retrieval_answer(question)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True,port=config.app.get('port'))
