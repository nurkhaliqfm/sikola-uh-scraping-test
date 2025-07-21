import asyncio
import csv
import glob
import json
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

async def get_data_mahasiswa(current_date, filePath, headers, nullMahasiswa, id_kelas):
    id_kelas = filePath.split("/")[3].split(".")[0].split("\\")[1]
    
    print(filePath)
    
    with open(filePath, "r", encoding="utf-8") as f:
        data = f.read()

    dataJson = json.loads(data)
    
    for i in range(0, len(dataJson)):
        logs = dataJson[i]["attendance_log"]
        if len(logs) == 0:
            print(len(logs), id_kelas, current_date)
            retries = 3
            for attempt in range(retries):
                try:
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
                        print("MAHASISWA ", current_date, id_kelas)

                        id_prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['id']
                        nama_kelas = response_data['kelasKuliah']['nama']
                        prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['nama_resmi']
                        nama_fakultas = next((p['fakultas']['nama_resmi'] for p in response_fakultas_data['prodis'] if p['id'] == id_prodi), None)

                        nullMahasiswa.append([current_date, id_kelas, nama_kelas, prodi, nama_fakultas, "PRESENSI BELUM DIISI/DOUBLE"])
                        break  # Exit the retry loop if successful
                except Exception as e:
                    print(f"Error fetching data for id_kelas MAHASISWA = {current_date} {id_kelas}: {e}")
                    if attempt == retries - 1:
                        print(f"Failed to fetch data for id_kelas MAHASISWA = {current_date} {id_kelas} after {retries} attempts")

    #     try:
    #         print("MAHASISWA ", current_date, id_kelas)
    #         async with aiohttp.ClientSession() as session:
    #             async with session.get(
    #                 f"{API_NEOSIA}/admin_mkpk/dosen/input_nilai/kelas_kuliah/{id_kelas}",
    #                 headers=headers,
    #                 ssl=False
    #             ) as response:
    #                 response_data = await response.json()
    #             async with session.get(
    #                 f"{API_NEOSIA}/admin_mkpk/prodi",
    #                 headers=headers,
    #                 ssl=False
    #             ) as response_fakultas:
    #                 response_fakultas_data = await response_fakultas.json()

    #             id_prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['id']
    #             nama_kelas = response_data['kelasKuliah']['nama']
    #             prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['nama_resmi']
    #             nama_fakultas = next((p['fakultas']['nama_resmi'] for p in response_fakultas_data['prodis'] if p['id'] == id_prodi), None)

    #             result_data.append([current_date, id_kelas, nama_kelas, prodi, nama_fakultas])
    #             break  # Exit the retry loop if successful
    #     except Exception as e:
    #         print(f"Error fetching data for id_kelas MAHASISWA = {current_date} {id_kelas}: {e}")
    #         if attempt == retries - 1:
    #             print(f"Failed to fetch data for id_kelas MAHASISWA = {current_date} {id_kelas} after {retries} attempts")
                
async def get_data_dosen(current_date, filePath, headers, nullDosen, id_kelas):
    
    with open(filePath, "r", encoding="utf-8") as f:
        data = f.read()
        
    # print(filePath)

    dataJson = json.loads(data)
    
    for i in range(0, len(dataJson)):
        logs = dataJson[i]["attendance_log"]
        if len(logs) == 0:
            print(len(logs), id_kelas, current_date)
            retries = 3
            for attempt in range(retries):
                try:
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
                        print("DOSEN ", current_date, id_kelas)

                        nama_kelas = response_data['kelasKuliah']['nama']
                        prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['nama_resmi']
                        nama_fakultas = next((p['fakultas']['nama_resmi'] for p in response_fakultas_data['prodis'] if p['id'] == id_prodi), None)

                        nullDosen.append([current_date, id_kelas, nama_kelas, prodi, nama_fakultas, "PRESENSI BELUM DIISI/DOUBLE"])
                        break  # Exit the retry loop if successful
                
                except Exception as e:
                    print(f"Error fetching data for id_kelas DOSEN = {current_date} {id_kelas}: {e}")
                    if attempt == retries - 1:
                        print(f"Failed to fetch data for id_kelas DOSEN = {current_date} {id_kelas} after {retries} attempts")

async def get_attendance():
    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjVlN2I2YzFmNjIwMmY3YWY2NTM3YTAwYTM0MjI1NDhhMGMyZDI1OTU3OWE3ZjBiYzEyMDM0YzNmNTk5ZTNjNWI2ZDhlOWViZDg0YWQzYjBhIn0.eyJhdWQiOiIyIiwianRpIjoiNWU3YjZjMWY2MjAyZjdhZjY1MzdhMDBhMzQyMjU0OGEwYzJkMjU5NTc5YTdmMGJjMTIwMzRjM2Y1OTllM2M1YjZkOGU5ZWJkODRhZDNiMGEiLCJpYXQiOjE3MTQ2MTY1MjcsIm5iZiI6MTcxNDYxNjUyNywiZXhwIjoxNzE1MDQ4NTI3LCJzdWIiOiI4NTQ5NiIsInNjb3BlcyI6WyIqIl19.fT5_vUnZJW1AKqZnV84_x2xXgN3DjPY4Gjf9zmls9MEEN_68fGBQKQLv1YO9C6y5FSKqGl50SHOPGTXPhFEw_KtIEOBn1NRAwq2TlUnpGlh4DDoPf87aAfOeCnC06zlU4UP4W8F73iY7ovjHeAsTYwyigvlSuKGEcv7Y1zCAXUL8g7UgIgpKS9cp5BHdI2Veo8_HZhyoxLDcwqlyc0dDIP17ax8w0LG3cpi4IkE_D_qUvziYGooIW0rkKFKV3-n2kVu1kjsVMbrlLEynQ2XOqouTR9F9GH7cEuL0527fhUkhpOD0snwFTGLfPJ4Eu98gFloMQIQQJau7MX3jNRwpdfWihulGgnzioDFz7h4JJ3gsC3C7XtTV0rq_oSQliZjVf9_gGALR2fYM6kuZ1MLWB23cBugP9JUeMKMcpob7UNO8akRiZxwg8XMtx0ZJB1hPaOukM81iILfZQqwnK62_G1eeivrFo_VRy7-P9U0A5CtKw-nKVtdGOZqVKwFSslbDPepAZyQbJls8OO2NAFzqhBtPrb5KxMPye_w3u0RZHEkSdpe_ZzIpsMNpV1P8S8s-0mZGUI-4Sdgb9DZy3Kd1FZFDiiP6fkAmThypU2nFilc0k-NVg-rn1XJp46fmrpWU6WnbDRDEzaLy2n1RAPLj2I2B1BpNRnQl2DvujQTf4JA",
        "Cookie": "XSRF-TOKEN=eyJpdiI6IjhjdUdjRXp4SFA0T0ZNZG1XenhvT2c9PSIsInZhbHVlIjoiMXNHMmtcL0ZXaHFpVFREdzJRRW1jSkR0VDNzYUhhSWZaU0NUd0VRRExIMjI2SUhyREVJRllQKzNqMTBMbXo0aHNmMmVzc05wYUJWckpDbDM1RDE0QXRhekNva0dmNHd3TytyODlodUd6R2tzN3kwWjRVNGlqc0JzXC85bFJ4TUpyMiIsIm1hYyI6ImNlMDMxMzY0OWRkNzAyYTljOWE5MDg0NjMzOGZiZGVhY2MyYTRhZTNmOGQzN2VhMzcyOTM2NTdhNGQ4OTdhNzkifQ%3D%3D; api_neosia_unhas_session=eyJpdiI6ImJpVDdvd3c0M0FXNDJhRk9ZanhzbUE9PSIsInZhbHVlIjoiVzFRTkxWbGRhMTI4S2llY1F3ZHhSRFptUWVYdjBOazB1NGFEd09PU1N6M21JQ3N2RUNRTXI0NXphRWZHeTRsTWdZZ1ZwZUhZcjhoY2NwY3FqM2xNVDg3SHBXVkxaMVk1WCs2NUgzNUlqZEc5Qkl2NjgwOThtN2ZuN3owMm1YVVoiLCJtYWMiOiI1OTc4ZGEyY2JkMGJkN2YwNWQ4NGJiOWQ4M2Q0NDQ5Mjk4ZTQzZDQwMDYzYjMwMDgzNjNhZTJlMmY0NGE4ZDY3In0%3D",
    }

    start_date = "2024-04-01"
    end_date = "2024-04-30"
    
    start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    lecturer_folder = "data/attendanceRaw"
    result_folder = "data/cekPresensi/null"

    os.makedirs(result_folder, exist_ok=True)

    nullMahasiswa = []
    nullDosen = []

    tasks = []
    for date_obj in range((end_date_obj - start_date_obj).days + 1):
        current_date = (start_date_obj + datetime.timedelta(days=date_obj)).strftime("%Y-%m-%d")
        listDosen = glob.glob(
            f"data/absensi/{current_date}/dosen/*.json"
        )
        listMahasiswa = glob.glob(
            f"data/absensi/{current_date}/mahasiswa/*.json"
        )

        for filePath in listMahasiswa:
            id_kelas = filePath.split("/")[3].split(".")[0].split("\\")[1]

            tasks.append(get_data_mahasiswa(current_date, filePath, headers, nullMahasiswa, id_kelas))
            
        
        for filePath in listDosen:
            id_kelas = filePath.split("/")[3].split(".")[0].split("\\")[1]

            tasks.append(get_data_dosen(current_date, filePath, headers, nullDosen, id_kelas))
    
    await asyncio.gather(*tasks)

    with open(f"{result_folder}/nullInMahasiswa-{start_date}-{end_date}.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["tanggal_rencana","id_kelas", 'nama_kelas', 'prodi', 'nama_fakultas', 'keterangan'])
        writer.writerows(nullMahasiswa)
        
    with open(f"{result_folder}/nullInDosen-{start_date}-{end_date}.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["tanggal_rencana","id_kelas", 'nama_kelas', 'prodi', 'nama_fakultas', 'keterangan'])
        writer.writerows(nullDosen)


if __name__ == '__main__':
    asyncio.run(get_attendance())
