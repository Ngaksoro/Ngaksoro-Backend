import os
from flask import Flask, request, jsonify
from google.cloud import storage
from google.oauth2 import service_account
from datetime import datetime


app = Flask(__name__)
key_path = 'ngaksoro-key.json'
credentials = service_account.Credentials.from_service_account_file(
    key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
storage_client = storage.Client(credentials=credentials)
bucket_name = 'ngaksoro'
folder_png = 'aksarajawa'
folder_gif = 'assetgif'


@app.route('/upload', methods=['POST'])
def upload_file():
    # Menerima file gambar dari permintaan POST
    image_file = request.files['file']
    # Mendapatkan timestamp saat ini
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # Menyimpan file gambar di bucket Google Cloud Storage
    file_extension = image_file.filename.rsplit('.', 1)[1]  # Mendapatkan ekstensi file
    file_name = f"{timestamp}.{file_extension}"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"ml/{file_name}")
    blob.upload_from_file(image_file)

    return 'File gambar berhasil diunggah ke bucket'


@app.route('/image/<filename>', methods=['GET'])
def get_image_url(filename):
    # Membuat URL file gambar dari bucket Google Cloud Storage
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(filename)
    return jsonify({'images': 'https://storage.googleapis.com/ngaksoro/aksarajawa/'+ blob.name.lower() +'.png',
                    'gif': 'https://storage.googleapis.com/ngaksoro/assetgif/'+ blob.name.lower() +'.gif'
                    })

@app.route('/assets', methods=['GET'])
def list_files():
    # Mendapatkan daftar nama file dari bucket Google Cloud Storage
    bucket = storage_client.bucket(bucket_name)
    image_png = bucket.list_blobs(prefix=folder_png)
    image_gif = bucket.list_blobs(prefix=folder_gif)
    png_list = []
    gif_list = []
    for x in image_png:
        png_link = 'https://storage.googleapis.com/{}/{}'.format(bucket_name, x.name)
        png_name = x.name.split("/")[1].split(".")[0]
        png_data = {'image': png_link, 'text': png_name}
        png_list.append(png_data)
    for y in image_gif:
        gif_link = 'https://storage.googleapis.com/{}/{}'.format(bucket_name, y.name)
        gif_name = y.name.split("/")[1].split(".")[0]
        gif_data = {'image': gif_link, 'text': gif_name}
        gif_list.append(gif_data)
    response = {
        'images': png_list,
        'gif': gif_list,
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))