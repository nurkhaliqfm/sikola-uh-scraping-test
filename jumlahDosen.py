import aiohttp
import asyncio
import os
import json
import pickle
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from urllib3.exceptions import InsecureRequestWarning
import requests
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def load_backup(file_name):
    if os.path.exists(file_name):
        with open(file_name, "rb") as f:
            return pickle.load(f)
    return None

def save_backup(file_name, processed_prodi, fakultas_data):
    with open(file_name, "wb") as f:
        pickle.dump({
            "processed_prodi": processed_prodi,
            "fakultas_data": fakultas_data
        }, f)

BASE_URL = "https://sikola-v2.unhas.ac.id"

async def get_dosen_status(session, baseUrl, course_id, dosen_status_dict):
    paramsEnroll = {
        "wsfunction": "core_enrol_get_enrolled_users",
        "courseid": course_id,
    }
    responseUser = await session.get(baseUrl, params=paramsEnroll, ssl=False)
    dataUser = await responseUser.json()

    for user in dataUser:
        if 'roles' in user:
            for role in user['roles']:
                # role 3 = dosen/lecturer
                if role['roleid'] == 3:
                    idnumber = user.get('idnumber')
                    if idnumber:
                        # Jika dosen belum pernah dicatat, catat statusnya
                        if idnumber not in dosen_status_dict:
                            dosen_status_dict[idnumber] = user.get('firstaccess', 0) > 0
                        # Jika sudah pernah dicatat dan sekarang ditemukan aktif, update ke aktif
                        elif not dosen_status_dict[idnumber] and user.get('firstaccess', 0) > 0:
                            dosen_status_dict[idnumber] = True

async def process_course(session, baseUrl, course, dosen_status_dict):
    course_id = course["id"]
    await get_dosen_status(session, baseUrl, course_id, dosen_status_dict)

async def fetch_sikola_course():
    async with aiohttp.ClientSession() as session:
        active_semester = "TA242"
        backup_file = "jumlahDosenAktif-21Jun-TA242.pkl"

        backup_data = load_backup(backup_file)
        processed_prodi = set()
        fakultas_data = {}

        if backup_data:
            processed_prodi = set(backup_data.get("processed_prodi", []))
            fakultas_data = backup_data.get("fakultas_data", {})

        with open("data/prodi_semester.json", "r", encoding="utf-8") as faculty_file:
            datafakultasProdi = json.load(faculty_file)

        for prodi in datafakultasProdi["prodis"]:
            nama_prodi = prodi["nama_resmi"]
            idnumberPordi = prodi["kode_dikti"]
            if nama_prodi in processed_prodi:
                continue

            fakultas = prodi["fakultas"]["nama_resmi"]

            # Request kategori berdasarkan prodi
            param_prodi = {
                "wsfunction": "core_course_get_categories",
                "criteria[0][key]": "name",
                "criteria[0][value]": nama_prodi,
            }
            response = await session.get(BASE_URL + "/webservice/rest/server.php?wstoken=3bdff39b5f62204b247c93e852caad8b&moodlewsrestformat=json", params=param_prodi, ssl=False)
            response = await response.json()
            if not response:
                continue

            param_prodi_courses = {
                "wsfunction": "core_course_get_courses_by_field",
                "field": "category",
                "value": response[0]["id"],
            }
            response = await session.get(BASE_URL + "/webservice/rest/server.php?wstoken=3bdff39b5f62204b247c93e852caad8b&moodlewsrestformat=json", params=param_prodi_courses, ssl=False)
            result_course = await response.json()
            
            filtered_courses = []
            for course in result_course["courses"]:
                if active_semester in course["shortname"]:
                    if '.' in course['idnumber']:
                        id_kelas = course['idnumber'].split(".")[1]
                        detail_kelas_path = f"data/detailKelas/TA242.8/{id_kelas}.json"
                        if os.path.exists(detail_kelas_path):
                            with open(detail_kelas_path, "r", encoding="utf-8") as kelas_file:
                                isiKelas = json.load(kelas_file)
                                if isiKelas['id_kelas_kuliah_jenis'] == 1:
                                    filtered_courses.append(course)

            dosen_status_dict = {}  # key: idnumber, value: True(aktif) / False(tidak aktif)
            for course in filtered_courses:
                await process_course(session, BASE_URL + "/webservice/rest/server.php?wstoken=3bdff39b5f62204b247c93e852caad8b&moodlewsrestformat=json", course, dosen_status_dict)

            jumlah_dosen_aktif = sum(1 for status in dosen_status_dict.values() if status)
            jumlah_dosen_tidak_aktif = sum(1 for status in dosen_status_dict.values() if not status)
            total_dosen = jumlah_dosen_aktif + jumlah_dosen_tidak_aktif
            persentase_aktif = (jumlah_dosen_aktif / total_dosen * 100) if total_dosen else 0
            persentase_tidak_aktif = (jumlah_dosen_tidak_aktif / total_dosen * 100) if total_dosen else 0

            if fakultas not in fakultas_data:
                fakultas_data[fakultas] = [0, 0, 0, 0.0, 0.0]
            fakultas_data[fakultas][0] += total_dosen
            fakultas_data[fakultas][1] += jumlah_dosen_aktif
            fakultas_data[fakultas][2] += jumlah_dosen_tidak_aktif
            fakultas_data[fakultas][3] = persentase_aktif
            fakultas_data[fakultas][4] = persentase_tidak_aktif

            processed_prodi.add(nama_prodi)
            print(f"{nama_prodi}: Aktif={jumlah_dosen_aktif}, Tidak Aktif={jumlah_dosen_tidak_aktif}, Total={total_dosen}")

            # Backup setiap selesai satu prodi
            save_backup(backup_file, list(processed_prodi), fakultas_data)

        # Buat DataFrame dari data fakultas
        fakultas_list = []
        for fakultas, (total_dosen, jumlah_aktif, jumlah_tidak_aktif, persen_aktif, persen_tidak_aktif) in fakultas_data.items():
            fakultas_list.append([
                fakultas,
                total_dosen,
                jumlah_aktif,
                jumlah_tidak_aktif,
                round(persen_aktif, 2),
                round(persen_tidak_aktif, 2)
            ])

        df = pd.DataFrame(
            fakultas_list,
            columns=[
                "Nama Fakultas",
                "Jumlah Dosen Unik",
                "Jumlah Dosen Aktif",
                "Jumlah Dosen Tidak Aktif",
                "Persentase Aktif (%)",
                "Persentase Tidak Aktif (%)"
            ],
        )

        # Tulis ke file Excel
        with pd.ExcelWriter("jumlah_dosen_aktif_perFakultas_TA242.xlsx") as writer:
            df.to_excel(writer, sheet_name="Fakultas", index=False)

            workbook = writer.book
            worksheet = writer.sheets["Fakultas"]

            # Atur lebar kolom
            for col in worksheet.columns:
                max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
                worksheet.column_dimensions[col[0].column_letter].width = max(15, max_length)

            worksheet.freeze_panes = "A2"

        if os.path.exists(backup_file):
            os.remove(backup_file)

if __name__ == "__main__":
    asyncio.run(fetch_sikola_course())