from flask import Flask, request, jsonify
import os
import easyocr

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize EasyOCR reader
try:
    reader = easyocr.Reader(['en'], gpu=True)  # Use GPU if available
    print("✅ EasyOCR Model Loaded Successfully!")
except Exception as e:
    print(f"❌ Error initializing EasyOCR: {e}")
    reader = None

@app.route('/')
def home():
    return jsonify({"message": "Text Extraction API is running!"})

@app.route('/extract-text', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file found in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        file.save(file_path)
        print(f"✅ File saved: {file_path}")
        
        # Perform OCR
        result = reader.readtext(file_path)
        extracted_text = [text for _, text, prob in result if prob >= 0.1]  # Confidence threshold 0.1
        
        # Print extracted text in terminal
        print(f"🔍 Extracted Text: {extracted_text}")

        # Delete the file after processing
        os.remove(file_path)
        print(f"🗑️ Deleted File: {file_path}")

        if not extracted_text:
            return jsonify({'extracted_text': [], 'message': 'No text detected. Try another image.'})

        return jsonify({'extracted_text': extracted_text})  # Send extracted text to frontend

    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return jsonify({'error': 'Error processing the image. Ensure it is a clear image with text.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
