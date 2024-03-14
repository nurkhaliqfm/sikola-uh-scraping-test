from flask import Flask, request, jsonify, render_template
import os
import requests
import csv

from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

NEOSIA_OAUTH_ACCESS_URL = os.getenv('NEOSIA_OAUTH_ACCESS_URL')
NEOSIA_OAUTH_CLIENT_ID = os.getenv('NEOSIA_OAUTH_CLIENT_ID')
NEOSIA_OAUTH_CLIENT_SECRET = os.getenv('NEOSIA_OAUTH_CLIENT_SECRET')
NEOSIA_ADMIN_MKPK_USERNAME = os.getenv('NEOSIA_ADMIN_MKPK_USERNAME')
NEOSIA_ADMIN_MKPK_PASSWORD = os.getenv('NEOSIA_ADMIN_MKPK_PASSWORD')
API_NEOSIA = os.getenv('API_NEOSIA')
TOKEN = os.getenv('TOKEN')

# Mock authentication credentials (replace with actual credentials)


def authenticate(username, password):
    return username == NEOSIA_ADMIN_MKPK_USERNAME and password == NEOSIA_ADMIN_MKPK_USERNAME

@app.route('/auth', methods=['POST'])
def auth():
    if request.method == 'POST':
        
        response = requests.post(NEOSIA_OAUTH_ACCESS_URL, data={
            'grant_type': 'password',
            'client_id': NEOSIA_OAUTH_CLIENT_ID,
            'client_secret': NEOSIA_OAUTH_CLIENT_SECRET,
            'username': NEOSIA_ADMIN_MKPK_USERNAME,
            'password': NEOSIA_ADMIN_MKPK_PASSWORD,
            'scope': '*'
        })

        if response.status_code == 200:
            access_token = response.json().get('access_token')
            # Store the access_token or use it as needed
            return jsonify({'message': 'Authentication successful', 'access_token': access_token}), 200
        else:
            return jsonify({'message': 'Authentication failed'}), 401

    return response.json()


@app.route('/attendance', methods=['GET'])
def get_attendance():
    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Authorization": f"Bearer {TOKEN}"
    }


    date_folder = "2024-02-19"
    dosen_folder = f"data/attendanceRaw/{date_folder}/dosen"
    mahasiswa_folder = f"data/attendanceRaw/{date_folder}/mahasiswa"
    result_folder_dosen = f"data/cekPresensi"
    result_folder_mahasiswa = f"data/cekPresensi"
    
    os.makedirs(result_folder_dosen, exist_ok=True)
    os.makedirs(result_folder_mahasiswa, exist_ok=True)

    dosen_files = os.listdir(dosen_folder)
    mahasiswa_files = os.listdir(mahasiswa_folder)

    dosen_id_kelas = [filename.split(".")[0] for filename in dosen_files]
    mahasiswa_id_kelas = [filename.split(".")[0] for filename in mahasiswa_files]
    not_in_mahasiswa = [filename for filename in dosen_id_kelas if filename not in mahasiswa_id_kelas]

    # if not_in_mahasiswa:
    not_in_mahasiswa_data = []
    for id_kelas in not_in_mahasiswa:
        try:
            print(id_kelas)
            response = requests.get(
                f"{API_NEOSIA}/admin_mkpk/dosen/input_nilai/kelas_kuliah/{id_kelas}",
                headers=headers
            )

            data = response.json()
            nama_kelas = data['kelasKuliah']['nama']
            prodi = data['kelasKuliah']['prodi_semester']['prodi']['nama_resmi']
            not_in_mahasiswa_data.append([id_kelas, nama_kelas, prodi])

        except ValueError:
            return jsonify({"message": "Error parsing JSON response"}), 500

    with open(f"data/cekPresensi/notInMahasiswa-{date_folder}.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["id_kelas", 'nama_kelas', 'prodi'])
        writer.writerows(not_in_mahasiswa_data)

          
    not_in_dosen = [filename for filename in mahasiswa_id_kelas if filename not in dosen_id_kelas]
    not_in_dosen_data = []

    for id_kelas in not_in_dosen:
        try:
            response = requests.get(
                f"{API_NEOSIA}/admin_mkpk/dosen/input_nilai/kelas_kuliah/{id_kelas}",
                headers=headers
            )

            data = response.json()
            nama_kelas = data['kelasKuliah']['nama']
            prodi = data['kelasKuliah']['prodi_semester']['prodi']['nama_resmi']
            not_in_dosen_data.append([id_kelas, nama_kelas, prodi])

        except ValueError:
            return jsonify({"message": "Error parsing JSON response"}), 500

    with open(f"data/cekPresensi/notInDosen-{date_folder}.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["id_kelas", 'nama_kelas', 'prodi'])
        writer.writerows(not_in_dosen_data)

    return jsonify({"message": "Done."})
if __name__ == '__main__':
    app.run(debug=True)
