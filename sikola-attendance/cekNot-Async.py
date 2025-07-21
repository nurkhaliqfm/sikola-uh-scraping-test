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

NEOSIA_OAUTH_ACCESS_URL = os.getenv("NEOSIA_OAUTH_ACCESS_URL")
NEOSIA_OAUTH_CLIENT_ID = os.getenv("NEOSIA_OAUTH_CLIENT_ID")
NEOSIA_OAUTH_CLIENT_SECRET = os.getenv("NEOSIA_OAUTH_CLIENT_SECRET")
NEOSIA_ADMIN_MKPK_USERNAME = os.getenv("NEOSIA_ADMIN_MKPK_USERNAME")
NEOSIA_ADMIN_MKPK_PASSWORD = os.getenv("NEOSIA_ADMIN_MKPK_PASSWORD")
API_NEOSIA = os.getenv("API_NEOSIA")
TOKEN = os.getenv("TOKEN")


async def authenticate(username, password):
    # Implement your authentication logic here
    return (
        username == NEOSIA_ADMIN_MKPK_USERNAME
        and password == NEOSIA_ADMIN_MKPK_PASSWORD
    )


async def get_data(current_date, id_kelas, headers, result_data):
    retries = 3
    for attempt in range(retries):
        try:
            print("MAHASISWA ", current_date, id_kelas)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{API_NEOSIA}/admin_mkpk/dosen/input_nilai/kelas_kuliah/{id_kelas}",
                    headers=headers,
                    ssl=False,
                ) as response:
                    response_data = await response.json()
                async with session.get(
                    f"{API_NEOSIA}/admin_mkpk/prodi", headers=headers, ssl=False
                ) as response_fakultas:
                    response_fakultas_data = await response_fakultas.json()

                id_prodi = response_data["kelasKuliah"]["prodi_semester"]["prodi"]["id"]
                nama_kelas = response_data["kelasKuliah"]["nama"]
                prodi = response_data["kelasKuliah"]["prodi_semester"]["prodi"][
                    "nama_resmi"
                ]
                nama_fakultas = next(
                    (
                        p["fakultas"]["nama_resmi"]
                        for p in response_fakultas_data["prodis"]
                        if p["id"] == id_prodi
                    ),
                    None,
                )

                result_data.append(
                    [
                        current_date,
                        id_kelas,
                        nama_kelas,
                        prodi,
                        nama_fakultas,
                        "JADWAL TIDAK SESUAI DENGAN PRESENSI DOSEN, NAMA INFO MATA KULIAH BERUBAH, NAMA PRESENSI BERUBAH, DAN TYPE GROUP PRESENSI TIDAK SESUAI",
                    ]
                )
                break  # Exit the retry loop if successful
        except Exception as e:
            print(
                f"Error fetching data for id_kelas MAHASISWA = {current_date} {id_kelas}: {e}"
            )
            if attempt == retries - 1:
                print(
                    f"Failed to fetch data for id_kelas MAHASISWA = {current_date} {id_kelas} after {retries} attempts"
                )


async def get_data_dosen(current_date, id_kelas, headers, result_data):
    retries = 3
    for attempt in range(retries):
        try:
            print("DOSEN ", current_date, id_kelas)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{API_NEOSIA}/admin_mkpk/dosen/input_nilai/kelas_kuliah/{id_kelas}",
                    headers=headers,
                    ssl=False,
                ) as response:
                    response_data = await response.json()
                async with session.get(
                    f"{API_NEOSIA}/admin_mkpk/prodi", headers=headers, ssl=False
                ) as response_fakultas:
                    response_fakultas_data = await response_fakultas.json()

                id_prodi = response_data["kelasKuliah"]["prodi_semester"]["prodi"]["id"]
                nama_kelas = response_data["kelasKuliah"]["nama"]
                prodi = response_data["kelasKuliah"]["prodi_semester"]["prodi"][
                    "nama_resmi"
                ]
                nama_fakultas = next(
                    (
                        p["fakultas"]["nama_resmi"]
                        for p in response_fakultas_data["prodis"]
                        if p["id"] == id_prodi
                    ),
                    None,
                )

                result_data.append(
                    [
                        current_date,
                        id_kelas,
                        nama_kelas,
                        prodi,
                        nama_fakultas,
                        "JADWAL TIDAK SESUAI DENGAN PRESENSI MHS, NAMA INFO MATA KULIAH BERUBAH, NAMA PRESENSI BERUBAH, DAN TYPE GROUP PRESENSI TIDAK SESUAI",
                    ]
                )
                break  # Exit the retry loop if successful
        except Exception as e:
            print(
                f"Error fetching data for id_kelas DOSEN = {current_date} {id_kelas}: {e}"
            )
            if attempt == retries - 1:
                print(
                    f"Failed to fetch data for id_kelas DOSEN = {current_date} {id_kelas} after {retries} attempts"
                )


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
    result_folder = "data/cekPresensi/not"

    os.makedirs(result_folder, exist_ok=True)

    result_data = []
    not_in_dosen_data = []

    tasks = []
    for date_obj in range((end_date_obj - start_date_obj).days + 1):
        current_date = (start_date_obj + datetime.timedelta(days=date_obj)).strftime(
            "%Y-%m-%d"
        )
        dosen_folder = f"{lecturer_folder}/{current_date}/dosen"
        mahasiswa_folder = f"{lecturer_folder}/{current_date}/mahasiswa"

        dosen_files = os.listdir(dosen_folder)
        mahasiswa_files = os.listdir(mahasiswa_folder)

        dosen_id_kelas = [filename.split(".")[0] for filename in dosen_files]
        mahasiswa_id_kelas = [filename.split(".")[0] for filename in mahasiswa_files]
        not_in_mahasiswa = [
            filename
            for filename in dosen_id_kelas
            if filename not in mahasiswa_id_kelas
        ]

        for id_kelas in not_in_mahasiswa:
            tasks.append(get_data(current_date, id_kelas, headers, result_data))

        not_in_dosen = [
            filename
            for filename in mahasiswa_id_kelas
            if filename not in dosen_id_kelas
        ]

        for id_kelas in not_in_dosen:
            tasks.append(
                get_data_dosen(current_date, id_kelas, headers, not_in_dosen_data)
            )

    await asyncio.gather(*tasks)

    with open(
        f"{result_folder}/notInMahasiswa-{start_date}-{end_date}.csv", "w", newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "tanggal_rencana",
                "id_kelas",
                "nama_kelas",
                "prodi",
                "nama_fakultas",
                "keterangan",
            ]
        )
        writer.writerows(result_data)

    with open(
        f"{result_folder}/notInDosen-{start_date}-{end_date}.csv", "w", newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "tanggal_rencana",
                "id_kelas",
                "nama_kelas",
                "prodi",
                "nama_fakultas",
                "keterangan",
            ]
        )
        writer.writerows(not_in_dosen_data)


if __name__ == "__main__":
    asyncio.run(get_attendance())
