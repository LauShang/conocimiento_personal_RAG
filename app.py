from flask import Flask, render_template, request, jsonify
import time

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

if __name__ == '__main__':
    app.run(debug=True)
