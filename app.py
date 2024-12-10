from flask import Flask, request, jsonify
from google.cloud import storage
import os

app = Flask(__name__)

# Initialize Google Cloud Storage Client
GCS_BUCKET_NAME = 'historyuser'
storage_client = storage.Client()


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Check if a file is included in the request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400

        file = request.files['file']

        # Check if the file has a valid filename
        if file.filename == '':
            return jsonify({'error': 'No file selected for upload'}), 400

        # Upload file to Google Cloud Storage
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(file.filename)
        blob.upload_from_file(file.stream)

        # Optionally, make the file publicly accessible
        blob.make_public()
        public_url = blob.public_url

        return jsonify({'message': 'File uploaded successfully', 'url': public_url}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def upload_to_gcs(local_file_path, destination_blob_name):
    try:
        # Access the bucket
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)

        # Upload the file
        blob.upload_from_filename(local_file_path)

        # Optionally, make the file publicly accessible
        blob.make_public()

        return blob.public_url

    except Exception as e:
        print(f"Error uploading file to GCS: {e}")
        return None

# Example Usage
local_file_path = "path/to/your/local/file.txt"
destination_blob_name = "my-file.txt"
uploaded_url = upload_to_gcs(local_file_path, destination_blob_name)
if uploaded_url:
    print(f"File successfully uploaded. Public URL: {uploaded_url}")
else:
    print("File upload failed.")   

if __name__ == '__main__':
    app.run(debug=True)
