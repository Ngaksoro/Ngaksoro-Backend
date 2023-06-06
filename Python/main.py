import os
from flask import Flask, request, jsonify
from google.cloud import storage
from google.oauth2 import service_account


app = Flask(__name__)
key_path = 'bucket-read.json'
credentials = service_account.Credentials.from_service_account_file(
    key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
storage_client = storage.Client(credentials=credentials)
bucket_name = 'ngaksoro'


@app.route('/upload', methods=['POST'])
def upload_file():
    # Menerima file gambar dari permintaan POST
    image_file = request.files['file']
    # Menyimpan file gambar di bucket Google Cloud Storage
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(image_file.filename)
    blob.upload_from_file(image_file)

    return 'File gambar berhasil diunggah ke bucket'


@app.route('/image/<filename>', methods=['GET'])
def get_image_url(filename):
    # Membuat URL file gambar dari bucket Google Cloud Storage
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(filename)
    # url = blob.generate_signed_url(expiration=300, method='GET')
    print(storage_client.bucket)

    return jsonify({'url': 'https://storage.googleapis.com/ngaksoro/'+ blob.name })

@app.route('/files', methods=['GET'])
def list_files():
    # Mendapatkan daftar nama file dari bucket Google Cloud Storage
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    file_list = []
    for blob in blobs:
        file_link = 'https://storage.googleapis.com/{}/{}'.format(bucket_name, blob.name)
        file_name = blob.name.split("/")[1].split(".")[0]
        file_data = {'image': file_link, 'text': file_name}
        file_list.append(file_data)
    response = {'images': file_list}

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
