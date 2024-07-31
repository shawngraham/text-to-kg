from flask import Flask, request, jsonify
from flask_cors import CORS
from paddleocr import PaddleOCR
import os
import pdf2image
import numpy as np
import io
from PIL import Image
import traceback

app = Flask(__name__)
CORS(app)

ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Initialize PaddleOCR

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Received a POST request.")
    if 'file' not in request.files:
        print("No file part in the request.")
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        print("No selected file.")
        return jsonify({'error': 'No selected file'}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return process_pdf(file_path)


def process_pdf(file_path):
    try:
        # Convert PDF to image(s)
        images = pdf2image.convert_from_path(file_path)
        full_text = ''

        for img in images:
            img_byte = io.BytesIO()
            img.save(img_byte, format='PNG')  # Save image as PNG format
            img_np = np.array(Image.open(img_byte))  # Convert to numpy array

            result = ocr.ocr(img_np)  # Perform OCR on the numpy array image
            for line in result:
                line_text = ' '.join([word[1][0] for word in line])
                full_text += line_text + '\n'

        return jsonify({'text': full_text}), 200
    except Exception as e:
        print("Error during PDF processing:")
        traceback.print_exc()  # Print full traceback for debugging
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)