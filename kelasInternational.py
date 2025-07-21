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

def save_backup(file_name, processed_prodi, prodi_data):
    with open(file_name, "wb") as f:
        pickle.dump({
            "processed_prodi": processed_prodi,
            "prodi_data": prodi_data
        }, f)

BASE_URL = "https://sikola-v2.unhas.ac.id"
KEYWORDS = ["international", "internasional", "inter"]

def is_international_course(course_name):
    name_lower = course_name.lower()
    return any(keyword in name_lower for keyword in KEYWORDS)

def format_nama_list(nama_list):
    return "\n".join([f"{i+1}. {nama}" for i, nama in enumerate(sorted(nama_list))]) if nama_list else ""

async def get_dosen_status_in_class(session, baseUrl, course_id):
    paramsEnroll = {
        "wsfunction": "core_enrol_get_enrolled_users",
        "courseid": course_id,
    }
    responseUser = await session.get(baseUrl, params=paramsEnroll, ssl=False)
    dataUser = await responseUser.json()
    dosen_aktif, dosen_tidak_aktif = [], []
    for user in dataUser:
        if 'roles' in user:
            for role in user['roles']:
                if role['roleid'] == 3:
                    fullname = user.get('fullname', '')
                    is_aktif = user.get('firstaccess', 0) > 0
                    if fullname:
                        if is_aktif and fullname not in dosen_aktif:
                            dosen_aktif.append(fullname)
                        elif not is_aktif and fullname not in dosen_tidak_aktif:
                            dosen_tidak_aktif.append(fullname)
    return dosen_aktif, dosen_tidak_aktif

async def fetch_sikola_course():
    async with aiohttp.ClientSession() as session:
        active_semester = "TA242"
        backup_file = "kelasInternational-21Jun-TA242.pkl"

        backup_data = load_backup(backup_file)
        processed_prodi = set()
        prodi_data = {}

        if backup_data:
            processed_prodi = set(backup_data.get("processed_prodi", []))
            prodi_data = backup_data.get("prodi_data", {})

        with open("data/prodi_semester.json", "r", encoding="utf-8") as faculty_file:
            datafakultasProdi = json.load(faculty_file)

        for prodi in datafakultasProdi["prodis"]:
            nama_prodi = prodi["nama_resmi"]
            idnumberPordi = prodi.get("kode_dikti")
            fakultas = prodi["fakultas"]["nama_resmi"]
            if nama_prodi in processed_prodi:
                continue

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

            kelas_international = []
            for course in result_course["courses"]:
                if active_semester in course["shortname"]:
                    course_name = course.get("fullname", "")
                    if is_international_course(course_name):
                        id_kelas = course['idnumber'].split(".")[1] if '.' in course['idnumber'] else None
                        detail_kelas_path = f"data/detailKelas/TA242.12/{id_kelas}.json" if id_kelas else None
                        if id_kelas and os.path.exists(detail_kelas_path):
                            dosen_aktif, dosen_tidak_aktif = await get_dosen_status_in_class(
                                session,
                                BASE_URL + "/webservice/rest/server.php?wstoken=3bdff39b5f62204b247c93e852caad8b&moodlewsrestformat=json",
                                course["id"]
                            )
                            jumlah_dosen_aktif = len(dosen_aktif)
                            jumlah_dosen_tidak_aktif = len(dosen_tidak_aktif)
                            total_dosen = jumlah_dosen_aktif + jumlah_dosen_tidak_aktif
                            persentase_aktif = (jumlah_dosen_aktif / total_dosen * 100) if total_dosen else 0
                            persentase_tidak_aktif = (jumlah_dosen_tidak_aktif / total_dosen * 100) if total_dosen else 0
                            kelas_international.append({
                                "Nama Prodi": nama_prodi,
                                "Nama Fakultas": fakultas,
                                "Nama Kelas": course_name,
                                "Nama Dosen Aktif": format_nama_list(dosen_aktif),
                                "Nama Dosen Tidak Aktif": format_nama_list(dosen_tidak_aktif),
                                "Jumlah Dosen": total_dosen,
                                "Jumlah Dosen Aktif": jumlah_dosen_aktif,
                                "Jumlah Dosen Tidak Aktif": jumlah_dosen_tidak_aktif,
                                "Persentase Aktif (%)": round(persentase_aktif, 2),
                                "Persentase Tidak Aktif (%)": round(persentase_tidak_aktif, 2)
                            })

            if kelas_international:
                prodi_data[nama_prodi] = kelas_international

            processed_prodi.add(nama_prodi)
            print(f"{nama_prodi}: {len(kelas_international)} kelas international")

            save_backup(backup_file, list(processed_prodi), prodi_data)

        # Tulis ke file Excel per sheet prodi (hanya yang ada kelas international)
        with pd.ExcelWriter("2024-2025 Genap list_dosen_international.xlsx") as writer:
            for nama_prodi, kelas_list in prodi_data.items():
                df = pd.DataFrame(kelas_list)
                df.to_excel(writer, sheet_name=nama_prodi[:31], index=False)

        if os.path.exists(backup_file):
            os.remove(backup_file)

if __name__ == "__main__":
    asyncio.run(fetch_sikola_course())