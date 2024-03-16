# from flask import Flask, request, jsonify, render_template
# import os
# import requests
# import csv

# from dotenv import load_dotenv

# app = Flask(__name__)
# load_dotenv()

# NEOSIA_OAUTH_ACCESS_URL = os.getenv('NEOSIA_OAUTH_ACCESS_URL')
# NEOSIA_OAUTH_CLIENT_ID = os.getenv('NEOSIA_OAUTH_CLIENT_ID')
# NEOSIA_OAUTH_CLIENT_SECRET = os.getenv('NEOSIA_OAUTH_CLIENT_SECRET')
# NEOSIA_ADMIN_MKPK_USERNAME = os.getenv('NEOSIA_ADMIN_MKPK_USERNAME')
# NEOSIA_ADMIN_MKPK_PASSWORD = os.getenv('NEOSIA_ADMIN_MKPK_PASSWORD')
# API_NEOSIA = os.getenv('API_NEOSIA')
# TOKEN = os.getenv('TOKEN')

# # Mock authentication credentials (replace with actual credentials)


# def authenticate(username, password):
#     return username == NEOSIA_ADMIN_MKPK_USERNAME and password == NEOSIA_ADMIN_MKPK_USERNAME

# @app.route('/auth', methods=['POST'])
# def auth():
#     if request.method == 'POST':
        
#         response = requests.post(NEOSIA_OAUTH_ACCESS_URL, data={
#             'grant_type': 'password',
#             'client_id': NEOSIA_OAUTH_CLIENT_ID,
#             'client_secret': NEOSIA_OAUTH_CLIENT_SECRET,
#             'username': NEOSIA_ADMIN_MKPK_USERNAME,
#             'password': NEOSIA_ADMIN_MKPK_PASSWORD,
#             'scope': '*'
#         })

#         if response.status_code == 200:
#             access_token = response.json().get('access_token')
#             # Store the access_token or use it as needed
#             return jsonify({'message': 'Authentication successful', 'access_token': access_token}), 200
#         else:
#             return jsonify({'message': 'Authentication failed'}), 401

#     return response.json()


# @app.route('/attendance', methods=['GET'])
# def get_attendance():
#     headers = {
#         "Content-Type": "application/json",
#         "Accept": "*/*",
#         "Authorization": f"Bearer {TOKEN}"
#     }


#     date_folder = "2024-02-23"
#     dosen_folder = f"data/attendanceRaw/{date_folder}/dosen"
#     mahasiswa_folder = f"data/attendanceRaw/{date_folder}/mahasiswa"
#     result_folder_dosen = f"data/cekPresensi"
#     result_folder_mahasiswa = f"data/cekPresensi"
    
#     os.makedirs(result_folder_dosen, exist_ok=True)
#     os.makedirs(result_folder_mahasiswa, exist_ok=True)

#     dosen_files = os.listdir(dosen_folder)
#     mahasiswa_files = os.listdir(mahasiswa_folder)

#     dosen_id_kelas = [filename.split(".")[0] for filename in dosen_files]
#     mahasiswa_id_kelas = [filename.split(".")[0] for filename in mahasiswa_files]
#     not_in_mahasiswa = [filename for filename in dosen_id_kelas if filename not in mahasiswa_id_kelas]

#     # if not_in_mahasiswa:
#     not_in_mahasiswa_data = []
#     for id_kelas in not_in_mahasiswa:
#         try:
#             print(id_kelas)
#             response = requests.get(
#                 f"{API_NEOSIA}/admin_mkpk/dosen/input_nilai/kelas_kuliah/{id_kelas}",
#                 headers=headers
#             )

#             data = response.json()
#             nama_kelas = data['kelasKuliah']['nama']
#             prodi = data['kelasKuliah']['prodi_semester']['prodi']['nama_resmi']
#             not_in_mahasiswa_data.append([id_kelas, nama_kelas, prodi])

#         except ValueError:
#             return jsonify({"message": "Error parsing JSON response"}), 500

#     with open(f"data/cekPresensi/notInMahasiswa-{date_folder}.csv", "w", newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(["id_kelas", 'nama_kelas', 'prodi'])
#         writer.writerows(not_in_mahasiswa_data)

          
#     not_in_dosen = [filename for filename in mahasiswa_id_kelas if filename not in dosen_id_kelas]
#     not_in_dosen_data = []

#     for id_kelas in not_in_dosen:
#         try:
#             response = requests.get(
#                 f"{API_NEOSIA}/admin_mkpk/dosen/input_nilai/kelas_kuliah/{id_kelas}",
#                 headers=headers
#             )

#             data = response.json()
#             nama_kelas = data['kelasKuliah']['nama']
#             prodi = data['kelasKuliah']['prodi_semester']['prodi']['nama_resmi']
#             not_in_dosen_data.append([id_kelas, nama_kelas, prodi])

#         except ValueError:
#             return jsonify({"message": "Error parsing JSON response"}), 500

#     with open(f"data/cekPresensi/notInDosen-{date_folder}.csv", "w", newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(["id_kelas", 'nama_kelas', 'prodi'])
#         writer.writerows(not_in_dosen_data)

#     return jsonify({"message": "Done."})
# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, request, jsonify, render_template
import os
import requests
import csv
import datetime

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

# @app.route('/auth', methods=['POST'])
# def auth():
#     if request.method == 'POST':
        
#         response = requests.post(NEOSIA_OAUTH_ACCESS_URL, data={
#             'grant_type': 'password',
#             'client_id': NEOSIA_OAUTH_CLIENT_ID,
#             'client_secret': NEOSIA_OAUTH_CLIENT_SECRET,
#             'username': NEOSIA_ADMIN_MKPK_USERNAME,
#             'password': NEOSIA_ADMIN_MKPK_PASSWORD,
#             'scope': '*'
#         })

#         if response.status_code == 200:
#             access_token = response.json().get('access_token')
#             # Store the access_token or use it as needed
#             return jsonify({'message': 'Authentication successful', 'access_token': access_token}), 200
#         else:
#             return jsonify({'message': 'Authentication failed'}), 401

#     return response.json()


# @app.route('/attendance', methods=['GET'])
def get_attendance():
    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Authorization": f"Bearer {TOKEN}"
    }

    start_date = "2024-02-19"
    end_date = "2024-03-13"
 
    start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    lecturer_folder = "data/attendanceRaw"
    student_folder = "data/attendanceRaw"
    result_folder = "data/cekPresensi"
    # result_folder_student = "data/cekPresensi/"
    
    os.makedirs(result_folder, exist_ok=True)
    # os.makedirs(result_folder_student, exist_ok=True)

    for date in range((end_date_obj - start_date_obj).days + 1):
        current_date = (start_date_obj + datetime.timedelta(days=date)).strftime("%Y-%m-%d")
        dosen_folder = f"{lecturer_folder}/{current_date}/dosen"
        mahasiswa_folder = f"{student_folder}/{current_date}/mahasiswa"

        dosen_files = os.listdir(dosen_folder)
        mahasiswa_files = os.listdir(mahasiswa_folder)

        dosen_id_kelas = [filename.split(".")[0] for filename in dosen_files]
        mahasiswa_id_kelas = [filename.split(".")[0] for filename in mahasiswa_files]
        not_in_mahasiswa = [filename for filename in dosen_id_kelas if filename not in mahasiswa_id_kelas]

        not_in_mahasiswa_data = []
        for id_kelas in not_in_mahasiswa:
            try:
                print("MAHASISWA ",current_date, id_kelas)
                response = requests.get(
                    f"{API_NEOSIA}/admin_mkpk/dosen/input_nilai/kelas_kuliah/{id_kelas}",
                    headers=headers
                )
               
                responseFakultas = requests.get(
                  f"{API_NEOSIA}/admin_mkpk/prodi",
                  headers=headers
                )
                data = response.json()
                data2 = responseFakultas.json()
                id_prodi =data['kelasKuliah']['prodi_semester']['prodi']['id']
                nama_kelas = data['kelasKuliah']['nama']
                prodi = data['kelasKuliah']['prodi_semester']['prodi']['nama_resmi']
                nama_fakultas = None
                for prodi_info in data2['prodis']:
                    if prodi_info['id'] == id_prodi:
                        nama_fakultas = prodi_info['fakultas']['nama_resmi']
                        break
                
                not_in_mahasiswa_data.append([current_date, id_kelas, nama_kelas, prodi, nama_fakultas])
              
            except ValueError:
                return jsonify({"message": "Error parsing JSON response"}), 500
        with open(f"{result_folder}/ListKendala-PresensiKelas-Mahasiswa ({start_date}-{end_date})-2.csv", "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["tanggal_rencana","id_kelas", 'nama_kelas', 'prodi','nama_fakultas'])
                writer.writerows(not_in_mahasiswa_data)

       

        not_in_dosen = [filename for filename in mahasiswa_id_kelas if filename not in dosen_id_kelas]
        not_in_dosen_data = []

        for id_kelas in not_in_dosen:
            try:
                print("DOSEN ",current_date, id_kelas)
                response = requests.get(
                    f"{API_NEOSIA}/admin_mkpk/dosen/input_nilai/kelas_kuliah/{id_kelas}",
                    headers=headers
                )
               
                responseFakultas = requests.get(
                  f"{API_NEOSIA}/admin_mkpk/prodi",
                  headers=headers
                )
                data = response.json()
                data2 = responseFakultas.json()
                id_prodi =data['kelasKuliah']['prodi_semester']['prodi']['id']
                nama_kelas = data['kelasKuliah']['nama']
                prodi = data['kelasKuliah']['prodi_semester']['prodi']['nama_resmi']
                nama_fakultas = None
                for prodi_info in data2['prodis']:
                    if prodi_info['id'] == id_prodi:
                        nama_fakultas = prodi_info['fakultas']['nama_resmi']
                        break

                not_in_dosen_data.append([current_date, id_kelas, nama_kelas, prodi, nama_fakultas])
               
            except ValueError:
                return jsonify({"message": f"Error parsing JSON response : {current_date} {id_kelas}"}), 500
        with open(f"{result_folder}/ListKendala-PresensiKelas-Dosen ({start_date}-{end_date})-2.csv", "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["tanggal_rencana","id_kelas", 'nama_kelas', 'prodi','nama_fakultas'])
                writer.writerows(not_in_dosen_data)
        # with open(f"{result_folder_student}/notInDosen-{current_date}.csv", "w", newline='') as file:
        #     writer = csv.writer(file)
        #     writer.writerow(["id_kelas", 'nama_kelas', 'prodi'])
        #     writer.writerows(not_in_dosen_data)
   
    
    return print("DONE...")

if __name__ == '__main__':
    get_attendance()


# import asyncio
# import csv
# import os
# from dotenv import load_dotenv
# import aiohttp
# import datetime


# load_dotenv()

# NEOSIA_OAUTH_ACCESS_URL = os.getenv('NEOSIA_OAUTH_ACCESS_URL')
# NEOSIA_OAUTH_CLIENT_ID = os.getenv('NEOSIA_OAUTH_CLIENT_ID')
# NEOSIA_OAUTH_CLIENT_SECRET = os.getenv('NEOSIA_OAUTH_CLIENT_SECRET')
# NEOSIA_ADMIN_MKPK_USERNAME = os.getenv('NEOSIA_ADMIN_MKPK_USERNAME')
# NEOSIA_ADMIN_MKPK_PASSWORD = os.getenv('NEOSIA_ADMIN_MKPK_PASSWORD')
# API_NEOSIA = os.getenv('API_NEOSIA')
# TOKEN = os.getenv('TOKEN')

# async def authenticate(username, password):
#     # Implement your authentication logic here
#     return username == NEOSIA_ADMIN_MKPK_USERNAME and password == NEOSIA_ADMIN_MKPK_PASSWORD

# async def get_data(current_date, id_kelas, headers, result_data):
#     async with aiohttp.ClientSession() as session:
#         try:
#             print(current_date, id_kelas)
#             async with session.get(
#                 f"{API_NEOSIA}/admin_mkpk/dosen/input_nilai/kelas_kuliah/{id_kelas}",
#                 headers=headers,
#                 ssl=False
#             ) as response:
#                 response_data = await response.json()
#             async with session.get(
#                 f"{API_NEOSIA}/admin_mkpk/prodi",
#                 headers=headers
#                 ,ssl=False
#             ) as response_fakultas:
#                 response_fakultas_data = await response_fakultas.json()

#             id_prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['id']
#             nama_kelas = response_data['kelasKuliah']['nama']
#             prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['nama_resmi']
#             nama_fakultas = next((p['fakultas']['nama_resmi'] for p in response_fakultas_data['prodis'] if p['id'] == id_prodi), None)

#             result_data.append([current_date, id_kelas, nama_kelas, prodi, nama_fakultas])
#         except Exception as e:
#             print(f"Error fetching data for id_kelas = {current_date} {id_kelas}: {e}")

# async def get_attendance():
#     headers = {
#         "Content-Type": "application/json",
#         "Accept": "*/*",
#         "Authorization": f"Bearer {TOKEN}"
#     }

#     start_date = "2024-02-19"
#     end_date = "2024-03-13"
    
#     start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
#     end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d")

#     lecturer_folder = "data/attendanceRaw"
#     result_folder = "data/cekPresensi"

#     os.makedirs(result_folder, exist_ok=True)

#     result_data = []

#     tasks = []
#     for date_obj in range((end_date_obj - start_date_obj).days + 1):
#         current_date = (start_date_obj + datetime.timedelta(days=date_obj)).strftime("%Y-%m-%d")
#         dosen_folder = f"{lecturer_folder}/{current_date}/dosen"
#         mahasiswa_folder = f"{lecturer_folder}/{current_date}/mahasiswa"

#         dosen_files = os.listdir(dosen_folder)
#         mahasiswa_files = os.listdir(mahasiswa_folder)

#         dosen_id_kelas = [filename.split(".")[0] for filename in dosen_files]
#         mahasiswa_id_kelas = [filename.split(".")[0] for filename in mahasiswa_files]
#         not_in_mahasiswa = [filename for filename in dosen_id_kelas if filename not in mahasiswa_id_kelas]

#         for id_kelas in not_in_mahasiswa:
#             tasks.append(get_data(current_date, id_kelas, headers, result_data))

#     await asyncio.gather(*tasks)

#     with open(f"{result_folder}/notInMahasiswa-{start_date}-{end_date}.csv", "w", newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(["tanggal_rencana","id_kelas", 'nama_kelas', 'prodi', 'nama_fakultas'])
#         writer.writerows(result_data)


# if __name__ == '__main__':
#     asyncio.run(get_attendance())
