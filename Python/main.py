import os
from flask import Flask, request, jsonify
from google.cloud import storage
from google.oauth2 import service_account
from datetime import datetime
from keras.utils import img_to_array, load_img
import matplotlib.image as mpimg
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import urllib.request
import random
import data_soal

app = Flask(__name__)
key_path = 'ngaksoro-key.json'
credentials = service_account.Credentials.from_service_account_file(
    key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
storage_client = storage.Client(credentials=credentials)
bucket_name = 'ngaksoro'
folder_asset = 'aksarajawa'
folder_ml = 'ml'
model_path = 'model.h5'
aksara_key = []

def preprocess_image(image_path):
    image = load_img(image_path, target_size=(150, 150))
    image = img_to_array(image) / 255.0  # Normalisasi nilai piksel antara 0 dan 1
    image = np.expand_dims(image, axis=0)  # Tambahkan dimensi batch
    return image

#Fungsi untuk memuat model
def load_model(model_path):
    model = tf.keras.models.load_model(model_path)
    return model

#Fungsi untuk melakukan prediksi
def predict_image(model, image):
    prediction = model.predict(image)
    return prediction

#Home gak jelas wkwk
@app.route('/', methods=['GET'])
def index():
    return 'Halo gaes'

@app.route('/soal', methods=['GET'])
def soal():
    for opsi in data_soal.data:
        opsi['opsi'] = []
    for item in data_soal.data:
        if len(item['opsi']) < 4 :
            opsis = item['opsi'] = item.get('opsi', [])
            opsis.append(item['jawaban'])  
            while len(opsis) < 4:
                random_value = random.choice(['ha', 'na', 'cha', 'ra', 'ka', 'da', 'ta', 'sa', 'wa', 'la', 'pa', 'dha', 'ja', 'ya', 'nya', 'ma', 'ga', 'ba', 'ta', 'nga'])
                if random_value not in opsis :
                    opsis.append(random_value)

            random.shuffle(opsis)
    return jsonify(data_soal.data)

#Upload file dari client dan disimpan ke dalam bucket
@app.route('/upload', methods=['POST'])
def upload_file():
    # Menerima file gambar dari permintaan POST
    image_file = request.files['file']
    aksara_text = request.form.get('aksara')
    # Mendapatkan timestamp saat ini
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # Menyimpan file gambar di bucket Google Cloud Storage
    file_extension = image_file.filename.rsplit('.', 1)[1]  # Mendapatkan ekstensi file
    file_name = f"{timestamp}.{file_extension}"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"ml/{file_name}")
    blob.upload_from_file(image_file)

    url_path = 'https://storage.googleapis.com/{}/{}'.format(bucket_name, f"ml/{file_name}")
    image_path = 'images.png'
    urllib.request.urlretrieve(url_path, image_path)

    model = tf.keras.models.load_model(model_path, compile=False)
    preprocessed_image = preprocess_image("images.png")
    prediction = predict_image(model, preprocessed_image)

    class_labels = ["ba", "ca", "da", "dha", 'ga', 'ha', 'ja', 'ka', 'la', 'ma', 'na', 'nga', 'nya', 'pa', 'ra', 'sa', 'ta', 'tha', 'wa', 'ya'] 
    predicted_class = np.argmax(prediction)
    predicted_label = class_labels[predicted_class]
    aksara_key.append(aksara_text)
    result = aksara_text.lower() == predicted_label
    response = {
        'result': result,
    }
    
    # blobs = bucket.list_blobs(prefix=folder_ml)

    # for blob in blobs:
    #     blob.delete()

    return jsonify(response)

#Menampilkan semua file yang telah di upload
@app.route('/ml-storage', methods=['GET'])
def ml_files():
    # Mendapatkan daftar nama file dari bucket Google Cloud Storage
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.list_blobs(prefix=folder_ml)
    file_list = []
    for x in blob:
        file_link = 'https://storage.googleapis.com/{}/{}'.format(bucket_name, x.name)
        file_data = {
            'assets': file_link,
            'key': aksara_key}
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

    aksara_key.clear()

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