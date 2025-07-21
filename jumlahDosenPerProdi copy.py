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

async def get_dosen_status(session, baseUrl, course_id, dosen_status_dict, dosen_fullname_dict):
    paramsEnroll = {
        "wsfunction": "core_enrol_get_enrolled_users",
        "courseid": course_id,
    }
    responseUser = await session.get(baseUrl, params=paramsEnroll, ssl=False)
    dataUser = await responseUser.json()

    for user in dataUser:
        if 'roles' in user:
            for role in user['roles']:
                if role['roleid'] == 3:
                    idnumber = user.get('idnumber')
                    fullname = user.get('fullname', '')
                    if idnumber:
                        # Simpan fullname jika belum ada
                        if idnumber not in dosen_fullname_dict and fullname:
                            dosen_fullname_dict[idnumber] = fullname
                        # Status aktif
                        is_aktif = user.get('firstaccess', 0) > 0
                        if idnumber not in dosen_status_dict:
                            dosen_status_dict[idnumber] = is_aktif
                        elif not dosen_status_dict[idnumber] and is_aktif:
                            dosen_status_dict[idnumber] = True

async def process_course(session, baseUrl, course, dosen_status_dict, dosen_fullname_dict):
    course_id = course["id"]
    await get_dosen_status(session, baseUrl, course_id, dosen_status_dict, dosen_fullname_dict)

async def fetch_sikola_course():
    async with aiohttp.ClientSession() as session:
        active_semester = "TA241"
        backup_file = "jumlahDosenAktif-21Jun-TA241.pkl"

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
            idnumberPordi = prodi.get("kode_dikti")
            if nama_prodi in processed_prodi:
                continue

            fakultas = prodi["fakultas"]["nama_resmi"]

            # Request kategori berdasarkan prodi
            param_prodi = {
                "wsfunction": "core_course_get_categories",
                "criteria[0][key]": "name",
                "criteria[0][value]": nama_prodi,
            }
            response = await session.get(
                BASE_URL + "/webservice/rest/server.php?wstoken=3bdff39b5f62204b247c93e852caad8b&moodlewsrestformat=json",
                params=param_prodi, ssl=False
            )
            response = await response.json()
            if not response or response[0].get("id") is None:
                continue

            param_prodi_courses = {
                "wsfunction": "core_course_get_courses_by_field",
                "field": "category",
                "value": str(response[0]["id"]),
            }
            response = await session.get(
                BASE_URL + "/webservice/rest/server.php?wstoken=3bdff39b5f62204b247c93e852caad8b&moodlewsrestformat=json",
                params=param_prodi_courses, ssl=False
            )
            result_course = await response.json()
            if "courses" not in result_course:
                continue

            filtered_courses = []
            for course in result_course["courses"]:
                if active_semester in course["shortname"]:
                    if '.' in course['idnumber']:
                        id_kelas = course['idnumber'].split(".")[1]
                        detail_kelas_path = f"data/detailKelas/TA241.19/{id_kelas}.json"
                        if os.path.exists(detail_kelas_path):
                            with open(detail_kelas_path, "r", encoding="utf-8") as kelas_file:
                                isiKelas = json.load(kelas_file)
                                if isiKelas.get('id_kelas_kuliah_jenis') == 1:
                                    filtered_courses.append(course)

            dosen_status_dict = {}
            dosen_fullname_dict = {}
            for course in filtered_courses:
                await process_course(
                    session,
                    BASE_URL + "/webservice/rest/server.php?wstoken=3bdff39b5f62204b247c93e852caad8b&moodlewsrestformat=json",
                    course,
                    dosen_status_dict,
                    dosen_fullname_dict
                )

            # Pisahkan dosen aktif dan tidak aktif
            dosen_aktif = [dosen_fullname_dict[idnum] for idnum, aktif in dosen_status_dict.items() if aktif and idnum in dosen_fullname_dict]
            dosen_tidak_aktif = [dosen_fullname_dict[idnum] for idnum, aktif in dosen_status_dict.items() if not aktif and idnum in dosen_fullname_dict]

            # Penomoran dan format nama
            def format_nama_list(nama_list):
                return "\n".join([f"{i+1}. {nama}" for i, nama in enumerate(sorted(nama_list))]) if nama_list else ""

            jumlah_dosen_aktif = len(dosen_aktif)
            jumlah_dosen_tidak_aktif = len(dosen_tidak_aktif)
            total_dosen = jumlah_dosen_aktif + jumlah_dosen_tidak_aktif
            persentase_aktif = (jumlah_dosen_aktif / total_dosen * 100) if total_dosen else 0
            persentase_tidak_aktif = (jumlah_dosen_tidak_aktif / total_dosen * 100) if total_dosen else 0

            if fakultas not in fakultas_data:
                fakultas_data[fakultas] = []
            fakultas_data[fakultas].append({
                "Nama Prodi": nama_prodi,
                "Nama Dosen Aktif": format_nama_list(dosen_aktif),
                "Nama Dosen Tidak Aktif": format_nama_list(dosen_tidak_aktif),
                "Jumlah Dosen": total_dosen,
                "Jumlah Dosen Aktif": jumlah_dosen_aktif,
                "Jumlah Dosen Tidak Aktif": jumlah_dosen_tidak_aktif,
                "Persentase Aktif (%)": round(persentase_aktif, 2),
                "Persentase Tidak Aktif (%)": round(persentase_tidak_aktif, 2)
            })

            processed_prodi.add(nama_prodi)
            print(f"{nama_prodi}: Aktif={jumlah_dosen_aktif}, Tidak Aktif={jumlah_dosen_tidak_aktif}, Total={total_dosen}")

            save_backup(backup_file, list(processed_prodi), fakultas_data)

        # Tulis ke file Excel per sheet fakultas
        with pd.ExcelWriter("2024-2025 Ganjil jumlah_dosen_aktif_perProdi_TA241.xlsx") as writer:
            for fakultas, prodi_list in fakultas_data.items():
                df = pd.DataFrame(prodi_list)
                df.to_excel(writer, sheet_name=fakultas[:31], index=False)

        if os.path.exists(backup_file):
            os.remove(backup_file)

if __name__ == "__main__":
    asyncio.run(fetch_sikola_course())