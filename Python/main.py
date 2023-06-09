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
folder_asset = 'aksarajawa'
folder_ml = 'ml'

@app.route('/', methods=['GET'])
def index():
    return 'Halo gaes'

#Upload file dari client dan disimpan ke dalam bucket
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

#Menampilkan semua file yang telah di upload
@app.route('/ml-storage', methods=['GET'])
def ml_files():
    # Mendapatkan daftar nama file dari bucket Google Cloud Storage
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.list_blobs(prefix=folder_ml)
    file_list = []
    for x in blob:
        file_link = 'https://storage.googleapis.com/{}/{}'.format(bucket_name, x.name)
        file_data = {'assets': file_link}
        file_list.append(file_data)
    response = {
        'images': file_list,
    }
    return jsonify(response)

#Menghapus semua file yang telah di upload
@app.route('/ml-destroy', methods=['GET'])
def delete_files():
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder_ml)

    for blob in blobs:
        blob.delete()

    return jsonify({'status': 'semua file telah dihapus'})

#Menampilkan file png dan gif sesuai dengan nama huruf aksara
# @app.route('/image/<filename>', methods=['GET'])
# def get_image_url(filename):
#     # Membuat URL file gambar dari bucket Google Cloud Storage
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(filename)
#     return jsonify({'images': 'https://storage.googleapis.com/ngaksoro/aksarajawa/'+ blob.name.lower() +'.png',
#                     'gif': 'https://storage.googleapis.com/ngaksoro/assetgif/'+ blob.name.lower() +'.gif'
#                     })

#Menampilkan semua file asset yang dibutuhkan android
@app.route('/assets', methods=['GET'])
def list_files():
    # Mendapatkan daftar nama file dari bucket Google Cloud Storage
    bucket = storage_client.bucket(bucket_name)
    image_folder = bucket.list_blobs(prefix=folder_asset)
    img_list = []
    aksara_order = ['ha', 'na', 'ca', 'ra','ka', 'da', 'ta', 'sa', 'wa', 'la', 'pa', 'dha', 'ja', 'ya', 'nya', 'ma', 'ga', 'ba', 'tha', 'nga']
    alphabet_order = []
    for x in image_folder:
        img_name = x.name.split("/")[1].split(".")[0]
        alphabet_order.append(img_name)
    for y in alphabet_order:
            index = alphabet_order.index(y)
            aksara_jawa_char = aksara_order[index]
            img_data = {
                'image': 'https://storage.googleapis.com/ngaksoro/aksarajawa/'+ aksara_jawa_char +'.png', 
                'gif': 'https://storage.googleapis.com/ngaksoro/assetgif/'+ aksara_jawa_char +'.gif',
                'text': aksara_jawa_char}
            img_list.append(img_data)
    response = {
        'images': img_list,
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))