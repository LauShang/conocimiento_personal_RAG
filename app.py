import os
import logging
import time
from flask import Flask, render_template, request, jsonify
from src.model_cp import PersonalKnowleged
from src.utils import (
    setup_logging,
    Config,
    download_youtube_audio_and_transcribe,
    generate_documents,
    )
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

@app.route('/process_youtube', methods=['POST'])
def process_youtube():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    # Download audio and transcribe
    transcription = download_youtube_audio_and_transcribe(url)
    # Generate documents
    documents = generate_documents(transcription=transcription, metadata={"source": url})
    # Add documents to the vector store
    model.add_documents(documents)
    return jsonify({"message": "Processing complete!", "transcription": transcription})

if __name__ == '__main__':
    app.run(debug=True,port=config.app.get('port'))
