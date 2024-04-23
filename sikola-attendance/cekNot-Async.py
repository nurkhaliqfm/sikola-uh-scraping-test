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

# async def get_data(current_date, id_kelas, headers, result_data):
#     async with aiohttp.ClientSession() as session:
#         try:
#             print("MAHASISWA ", current_date, id_kelas)
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
#             print(f"Error fetching data for id_kelas MAHASISWA = {current_date} {id_kelas}: {e}")
            
# async def get_data_dosen(current_date, id_kelas, headers, not_in_dosen_data):
#     async with aiohttp.ClientSession() as session:
#         try:
#             print("DOSEN ", current_date, id_kelas)
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

#             not_in_dosen_data.append([current_date, id_kelas, nama_kelas, prodi, nama_fakultas])
#         except Exception as e:
#             print(f"Error fetching data for id_kelas DOSEN = {current_date} {id_kelas}: {e}")

# async def get_attendance():
#     headers = {
#         "Content-Type": "application/json",
#         "Accept": "*/*",
#         "Authorization": f"Bearer {TOKEN}"
#     }

#     start_date = "2024-02-19"
#     end_date = "2024-02-23"
    
#     start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
#     end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d")

#     lecturer_folder = "data/attendanceRaw"
#     result_folder = "data/cekPresensi"

#     os.makedirs(result_folder, exist_ok=True)

#     result_data = []
#     not_in_dosen_data = []

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
            
#         not_in_dosen = [filename for filename in mahasiswa_id_kelas if filename not in dosen_id_kelas]
        
#         for id_kelas in not_in_dosen:
#             tasks.append(get_data_dosen(current_date, id_kelas, headers, not_in_dosen_data))
    
#     await asyncio.gather(*tasks)

#     with open(f"{result_folder}/notInMahasiswa-{start_date}-{end_date}.csv", "w", newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(["tanggal_rencana","id_kelas", 'nama_kelas', 'prodi', 'nama_fakultas'])
#         writer.writerows(result_data)
        
#     with open(f"{result_folder}/notInDosen-{start_date}-{end_date}.csv", "w", newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(["tanggal_rencana","id_kelas", 'nama_kelas', 'prodi', 'nama_fakultas'])
#         writer.writerows(not_in_dosen_data)


# if __name__ == '__main__':
#     asyncio.run(get_attendance())


import asyncio
import csv
import os
from dotenv import load_dotenv
import aiohttp
import datetime

load_dotenv()

NEOSIA_OAUTH_ACCESS_URL = os.getenv('NEOSIA_OAUTH_ACCESS_URL')
NEOSIA_OAUTH_CLIENT_ID = os.getenv('NEOSIA_OAUTH_CLIENT_ID')
NEOSIA_OAUTH_CLIENT_SECRET = os.getenv('NEOSIA_OAUTH_CLIENT_SECRET')
NEOSIA_ADMIN_MKPK_USERNAME = os.getenv('NEOSIA_ADMIN_MKPK_USERNAME')
NEOSIA_ADMIN_MKPK_PASSWORD = os.getenv('NEOSIA_ADMIN_MKPK_PASSWORD')
API_NEOSIA = os.getenv('API_NEOSIA')
TOKEN = os.getenv('TOKEN')

async def authenticate(username, password):
    # Implement your authentication logic here
    return username == NEOSIA_ADMIN_MKPK_USERNAME and password == NEOSIA_ADMIN_MKPK_PASSWORD

async def get_data(current_date, id_kelas, headers, result_data):
    retries = 3
    for attempt in range(retries):
        try:
            print("MAHASISWA ", current_date, id_kelas)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{API_NEOSIA}/admin_mkpk/dosen/input_nilai/kelas_kuliah/{id_kelas}",
                    headers=headers,
                    ssl=False
                ) as response:
                    response_data = await response.json()
                async with session.get(
                    f"{API_NEOSIA}/admin_mkpk/prodi",
                    headers=headers,
                    ssl=False
                ) as response_fakultas:
                    response_fakultas_data = await response_fakultas.json()

                id_prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['id']
                nama_kelas = response_data['kelasKuliah']['nama']
                prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['nama_resmi']
                nama_fakultas = next((p['fakultas']['nama_resmi'] for p in response_fakultas_data['prodis'] if p['id'] == id_prodi), None)

                result_data.append([current_date, id_kelas, nama_kelas, prodi, nama_fakultas, "JADWAL TIDAK SESUAI DENGAN PRESENSI DOSEN, NAMA INFO MATA KULIAH BERUBAH, NAMA PRESENSI BERUBAH, DAN TYPE GROUP PRESENSI TIDAK SESUAI"])
                break  # Exit the retry loop if successful
        except Exception as e:
            print(f"Error fetching data for id_kelas MAHASISWA = {current_date} {id_kelas}: {e}")
            if attempt == retries - 1:
                print(f"Failed to fetch data for id_kelas MAHASISWA = {current_date} {id_kelas} after {retries} attempts")
                
async def get_data_dosen(current_date, id_kelas, headers, result_data):
    retries = 3
    for attempt in range(retries):
        try:
            print("DOSEN ", current_date, id_kelas)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{API_NEOSIA}/admin_mkpk/dosen/input_nilai/kelas_kuliah/{id_kelas}",
                    headers=headers,
                    ssl=False
                ) as response:
                    response_data = await response.json()
                async with session.get(
                    f"{API_NEOSIA}/admin_mkpk/prodi",
                    headers=headers,
                    ssl=False
                ) as response_fakultas:
                    response_fakultas_data = await response_fakultas.json()

                id_prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['id']
                nama_kelas = response_data['kelasKuliah']['nama']
                prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['nama_resmi']
                nama_fakultas = next((p['fakultas']['nama_resmi'] for p in response_fakultas_data['prodis'] if p['id'] == id_prodi), None)

                result_data.append([current_date, id_kelas, nama_kelas, prodi, nama_fakultas, "JADWAL TIDAK SESUAI DENGAN PRESENSI MHS, NAMA INFO MATA KULIAH BERUBAH, NAMA PRESENSI BERUBAH, DAN TYPE GROUP PRESENSI TIDAK SESUAI"])
                break  # Exit the retry loop if successful
        except Exception as e:
            print(f"Error fetching data for id_kelas DOSEN = {current_date} {id_kelas}: {e}")
            if attempt == retries - 1:
                print(f"Failed to fetch data for id_kelas DOSEN = {current_date} {id_kelas} after {retries} attempts")

async def get_attendance():
    headers = {
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImZmNDQ4YzI2ODNhYjlmNThiNTIzMjE0ZDBlYmJjM2U5NWZmMzEzMzY1YjAyYWQxNWZiNjIyNzI2ZjNlNDIxMTAyYTcxMDhkMDRiYThhMDllIn0.eyJhdWQiOiIyIiwianRpIjoiZmY0NDhjMjY4M2FiOWY1OGI1MjMyMTRkMGViYmMzZTk1ZmYzMTMzNjViMDJhZDE1ZmI2MjI3MjZmM2U0MjExMDJhNzEwOGQwNGJhOGEwOWUiLCJpYXQiOjE3MTE3ODk2MzksIm5iZiI6MTcxMTc4OTYzOSwiZXhwIjoxNzEyMjIxNjM5LCJzdWIiOiI4NTQ5NiIsInNjb3BlcyI6WyIqIl19.QkfAFFW8XFKRETobbP2LTWEuDgPyiJwInSuxfPouWlibf-6l-MtkSkZvUKD-BZDIh0CtGLaWhL2yVZ-bLh1Iw0hec0S0f9u9hucrFmK7d-slgpXoqj65PdZbxF4GAT8WSnsD1_AizS3u_VO-UmuCkHL_h-ixE69Qi6LYO-DLj2BmA-7I5hNu7aNC9pxK55Bjvjqra4sUbXot_wgyhRsesEdHp9Zha8aCzMPBYSqBZAeNUjI144UCQhTSf9zirqEJkuiiWpl23bJjdervtnIhXLgyjHzeKhrdf_gVPBG5hABQ1Hh60Lo2v8VQQPUhfSJQHCr4px1O2O-PoMbNeZAouhKwR5qn0mQP1bZuTk4V_9KTPvTwvi80lS2gV_J1-tBYalfh0NZpGbQFFRord4J_4dRq_xX_7qu-Z-uzqc8a3x8iJFPeOYg48xFcI4KsGdifT6430f-JEPNbDs8DvhepnmU4ikLcvEhKefJmYLVix5rZXnBNkhp92PYOrHTofSDIuNYK0EJqqjVhV1u_4FsvInlj98FisOO1ZWbMQIWjqHgL3JnEqtQ366sdhc79k3Jm3NR6_CCDRapoAGI5LGyW6h2aGnAN1onuT7SqvVOtmttX_9bCGsJGUfYf3zQlkMAjKeb6afqHX1yuZ7VwupheJEzHtXnrOb1w9yuCcDtQNqU',
        'Cookie': 'XSRF-TOKEN=eyJpdiI6InFISllYUzFEbTE5OU1xd2FHNVZZOVE9PSIsInZhbHVlIjoiM3ZwSmh6b1wvZlgwUjJTZHdFMjllZXd3VUNlNFY3OEFqdG1xXC9JQVlBamtKV3ZGMjZtcklMUWpyeldjSE1JNXdUcVNDS0ViY3M5SnpUZzJrb3dyU1BpZjIrSDZiSkk2Snc3MVlQRW5zYitqVFVGSW0rd3ZhXC90STFOK3FTaU9adkEiLCJtYWMiOiI5NzlhYzc0MzY1ZTA0YWNkZGU3NzEyZDc5MTFkOWUwNGM0Y2M1MGRlMjNhOTVkYjhjODVlNWY1ZThjMjE1NjAxIn0%3D; api_neosia_unhas_session=eyJpdiI6IlU4WmdqXC9TYW5NWVVuSzdtbWpjMWN3PT0iLCJ2YWx1ZSI6IlZocmhBQkt4bEtSSDAyK3p4Nyt1R3RLMWVqdmJmQjgrV205OVlBbXN2eWRzXC9xVTltTXdhNlwvblNTVmw3bVhHNDlxb3RBbHFjVER4d0tZZER3MEkxeU16cGV3enN4YytoNjRNZUVoZzVlVlcrVE5vUFwvVVJ3bVwvcExsRUNYb3p4cSIsIm1hYyI6IjQ5ZGRmNmJmNjZiMDI5NDQ3ODUzYWRlMjQzNzE4YzcyNzA4OTVhM2JjNWU0NGE3ZDBlNDExZWNjNjA1NWE5NGUifQ%3D%3D'
    }

    start_date = "2024-03-16"
    end_date = "2024-03-31"
    
    start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    lecturer_folder = "data/attendanceRaw"
    result_folder = "data/cekPresensi/not"

    os.makedirs(result_folder, exist_ok=True)

    result_data = []
    not_in_dosen_data = []

    tasks = []
    for date_obj in range((end_date_obj - start_date_obj).days + 1):
        current_date = (start_date_obj + datetime.timedelta(days=date_obj)).strftime("%Y-%m-%d")
        dosen_folder = f"{lecturer_folder}/{current_date}/dosen"
        mahasiswa_folder = f"{lecturer_folder}/{current_date}/mahasiswa"

        dosen_files = os.listdir(dosen_folder)
        mahasiswa_files = os.listdir(mahasiswa_folder)

        dosen_id_kelas = [filename.split(".")[0] for filename in dosen_files]
        mahasiswa_id_kelas = [filename.split(".")[0] for filename in mahasiswa_files]
        not_in_mahasiswa = [filename for filename in dosen_id_kelas if filename not in mahasiswa_id_kelas]

        for id_kelas in not_in_mahasiswa:
            tasks.append(get_data(current_date, id_kelas, headers, result_data))
            
        not_in_dosen = [filename for filename in mahasiswa_id_kelas if filename not in dosen_id_kelas]
        
        for id_kelas in not_in_dosen:
            tasks.append(get_data_dosen(current_date, id_kelas, headers, not_in_dosen_data))
    
    await asyncio.gather(*tasks)

    with open(f"{result_folder}/notInMahasiswa-{start_date}-{end_date}.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["tanggal_rencana","id_kelas", 'nama_kelas', 'prodi', 'nama_fakultas', 'keterangan'])
        writer.writerows(result_data)
        
    with open(f"{result_folder}/notInDosen-{start_date}-{end_date}.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["tanggal_rencana","id_kelas", 'nama_kelas', 'prodi', 'nama_fakultas', 'keterangan'])
        writer.writerows(not_in_dosen_data)


if __name__ == '__main__':
    asyncio.run(get_attendance())
