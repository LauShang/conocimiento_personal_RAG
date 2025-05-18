import os
import logging
import time
import tempfile
from flask import Flask, render_template, request, jsonify
from src.model_cp import PersonalKnowleged
from src.utils import (
    setup_logging,
    Config,
    download_youtube_audio_and_transcribe,
    generate_documents,
    transcribe_audio,
    get_pdf,
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

@app.route('/process_mp3', methods=['POST'])
def process_mp3():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file.save(temp_file.name)
        temp_file_path = temp_file.name

    try:
        transcription = transcribe_audio(temp_file_path)
        # Generate documents
        documents = generate_documents(transcription=transcription, metadata={"source": temp_file_path})
        # Add documents to the vector store
        model.add_documents(documents)
        return jsonify({"message": "Processing complete!", "transcription": transcription})
    finally:
        os.remove(temp_file_path)

@app.route('/process_text', methods=['POST'])
def process_text():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Generate documents
    documents = generate_documents(transcription=text, metadata={"source": "user_input"})
    # Add documents to the vector store
    model.add_documents(documents)
    return jsonify({"message": "Processing complete!"})

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file.save(temp_file.name)
        temp_file_path = temp_file.name

    try:
        documents = get_pdf(temp_file_path)
        # Add documents to the vector store
        model.add_documents(documents)
        return jsonify({"message": "Processing complete!"})
    finally:
        os.remove(temp_file_path)

if __name__ == '__main__':
    app.run(debug=True,port=config.app.get('port'))
