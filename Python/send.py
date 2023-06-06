import requests

# Mengirim file gambar ke API
def send_image(file_path):
    url = "https://ngaksoro-s6jxliwbja-uc.a.run.app/upload"  # Ganti dengan URL API yang sesuai
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, files=files)
    print(response.text)

# Menjalankan fungsi send_image dengan file gambar
send_image('E:\Picture\klee-1.jpg')


