from flask import Flask, request, jsonify
from flask_cors import CORS
from paddleocr import PaddleOCR
import os
import pdf2image
import numpy as np
import io
from PIL import Image
import traceback
import requests

app = Flask(__name__)
CORS(app)

ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Initialize PaddleOCR

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return process_pdf(file_path)

def process_pdf(file_path):
    try:
        images = pdf2image.convert_from_path(file_path)
        full_text = ''

        for img in images:
            img_byte = io.BytesIO()
            img.save(img_byte, format='PNG')
            img_np = np.array(Image.open(img_byte))

            result = ocr.ocr(img_np)
            for line in result:
                line_text = ' '.join([word[1][0] for word in line])
                full_text += line_text + '\n'

        return jsonify({'text': full_text}), 200
    except Exception as e:
        print("Error during PDF processing:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/generate_ontology', methods=['POST'])
def generate_ontology():
    try:
        data = request.json
        ocr_text = data.get('ocrText')
        if not ocr_text:
            return jsonify({'error': 'No OCR text provided'}), 400

        system_prompt = "You are a linked knowledge representation assistant. Identify an ontology for actors, events, objects and organizations appropriate to the input text. Events should connect actors, organizations, or objects. Return ONLY the results as properly formatted high-quality json." \
                        "Example: Mary Turlington made a ceramic Ducky in Big Pond in 2023; she had Kenny Wong paint it. It was bought by the Grand Narrows Museum in 2023 for $123456." \
                        "Result:[{'nodes': [{'label': 'the Ducky','type': 'Object','madeIn': 'Big Pond','date': '2023','potter': 'Mary Turlington','painter': 'Kenny Wong','price': '$123456'}],'edges': [{'startNode': 'the Ducky','endNode': 'Grand Narrows Museum','type': 'bought by','date': '2024'}]}]"

        request_body = {
            "model": "gemma:7b",
            "prompt": f"{system_prompt}\n\n{ocr_text}",
            "stream": False
        }

        print("Sending request to remote service:", request_body)

        response = requests.post('http://localhost:11434/api/generate', headers={'Content-Type': 'application/json'}, json=request_body)

        print("Received response from remote service:", response.status_code, response.content)

        if not response.ok:
            raise Exception('Failed to generate ontology')

        ontology_response = response.json().get('response', 'No response field in the returned JSON')
        return jsonify({'ontology': ontology_response}), 200

    except Exception as e:
        print("Error generating ontology:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/generate_gexf', methods=['POST'])
def generate_gexf():
    try:
        data = request.json
        ontology_json = data.get('ontologyJson')
        if not ontology_json:
            return jsonify({'error': 'No ontology JSON provided'}), 400

        system_prompt = "Please transform the following json into HIGH QUALITY and WELL FORMED gexf for import into Gephi. Return ONLY VALID gexf formatted xml. This is important for my career. DO NOT WRAP THE RESULT IN BACK-TICKS. Use this template for formatting the xml <?xml version='1.0' encoding='UTF-8'?>\n<gexf xmlns='http://www.gexf.net/1.3' version='1.3'>\n    <meta lastmodifieddate='2023-10-02'>\n        <creator>Example Creator</creator>\n        <description>A simple GEXF file for one-shot learning</description>\n    </meta>\n    <graph mode='static' defaultedgetype='directed'>\n        <!-- Nodes definition -->\n        <nodes>\n            <node id='0' label='Node A'>\n                <attvalues>\n                    <attvalue for='degree' value='2'/>\n                </attvalues>\n            </node>\n            <node id='1' label='Node B'>\n                <attvalues>\n                    <attvalue for='degree' value='2'/>\n                </attvalues>\n            </node>\n            <node id='2' label='Node C'>\n                <attvalues>\n                    <attvalue for='degree' value='1'/>\n                </attvalues>\n            </node>\n        </nodes>\n        \n        <!-- Edges definition -->\n        <edges>\n            <edge id='0' source='0' target='1' label='Edge AB'>\n                <attvalues>\n                    <attvalue for='weight' value='1'/>\n                </attvalues>\n            </edge>\n            <edge id='1' source='1' target='2' label='Edge BC'>\n                <attvalues>\n                    <attvalue for='weight' value='1'/>\n                </attvalues>\n            </edge>\n        </edges>\n        \n        <!-- Attribute definitions -->\n        <attributes class='node'>\n            <attribute id='degree' title='degree' type='integer'/>\n        </attributes>\n        \n        <attributes class='edge'>\n            <attribute id='weight' title='weight' type='double'/>\n        </attributes>\n    </graph>\n</gexf>"

        request_body = {
            "model": "gemma:7b",
            "prompt": f"{system_prompt}\n\n{ontology_json}",
            "stream": False
        }

        print("Sending request to remote service:", request_body)

        response = requests.post('http://localhost:11434/api/generate', headers={'Content-Type': 'application/json'}, json=request_body)

        print("Received response from remote service:", response.status_code, response.content)

        if not response.ok:
            raise Exception('Failed to generate gexf')

        gexf_response = response.json().get('response', 'No response field in the returned JSON')
        return jsonify({'gexf': gexf_response}), 200

    except Exception as e:
        print("Error generating gexf:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)