from flask import Flask, request, jsonify
from google.cloud import storage, secretmanager
import os

app = Flask(__name__)

# Function to access secrets from Secret Manager
def access_secret_version(project_id, secret_id, version_id, save_to_file=False):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)

    secret_data = response.payload.data.decode("UTF-8")

    if save_to_file:
        # Save the secret data as a JSON file locally (temporary)
        with open("service_account.json", "w") as f:
            f.write(secret_data)

    return secret_data


# Retrieve and save JSON key from Secret Manager
PROJECT_ID = "agriscan-capstone-project"
SECRET_ID = "credentials"  # Your secret ID in Secret Manager
VERSION_ID = "latest"       # Typically "latest" for the most recent version
access_secret_version(PROJECT_ID, SECRET_ID, VERSION_ID, save_to_file=True)

# Set the environment variable for Google authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account.json"

# Initialize Google Cloud Storage client
storage_client = storage.Client()

# Retrieve bucket name (you can also store this in Secret Manager if needed)
bucket_name = "historyuser"  # Replace with your actual bucket name

# Flask route to upload files
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Check if file is included in the request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400

        file = request.files['file']

        # Check if the file has a valid filename
        if file.filename == '':
            return jsonify({'error': 'No file selected for upload'}), 400

        # Upload file to Google Cloud Storage
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file.filename)
        blob.upload_from_file(file)

        # Optionally, make the file publicly accessible
        blob.make_public()
        public_url = blob.public_url

        return jsonify({'message': 'File uploaded successfully', 'url': public_url}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
