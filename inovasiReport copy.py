import aiohttp
import asyncio
import os
import json
import pickle
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Disable InsecureRequestWarning
from urllib3.exceptions import InsecureRequestWarning
import requests
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Fungsi untuk memuat progres dari file backup
def load_backup(file_name):
    if os.path.exists(file_name):
        with open(file_name, "rb") as f:
            return pickle.load(f)
    return None


# Fungsi untuk menyimpan progres ke file backup
def save_backup(file_name, data):
    with open(file_name, "wb") as f:
        pickle.dump(data, f)


async def process_course(session, baseUrl, course, active_modules, no_active_modules, with_attendance, no_attendance):
    courseid = course["id"]
    
    param_course = {
        "wsfunction": "core_course_get_contents",
        "courseid": courseid,
    }
    response = await session.get(baseUrl, params=param_course, ssl=False)
    contents = await response.json()

    has_attendance = False  # Default value for has_attendance

    has_other_modules = any(
        isinstance(section, dict) and  # Ensure section is a dictionary
        "section" in section and
        "modules" in section and
        isinstance(section["modules"], list) and  # Ensure modules is a list
        section["section"] != 0 and
        len(section["modules"]) > 0 and
        any(isinstance(mod, dict) and "modname" in mod for mod in section["modules"])  # Ensure mod is a dictionary and has modname
        for section in contents
    ) and len(contents) > 1


    
    for section in contents:
        # Ensure section is a dictionary and has the "modules" key as a list
        if isinstance(section, dict) and "modules" in section and isinstance(section["modules"], list):
            for module in section["modules"]:
                # Ensure each module is a dictionary and has the "modname" key
                if isinstance(module, dict) and "modname" in module:
                    if module["modname"] == "attendance":
                        attendanceid = module["instance"]
                        param_attendance = {
                            "wsfunction": "mod_attendance_get_sessions",
                            "attendanceid": attendanceid,
                        }
                        session_response = await session.get(baseUrl, params=param_attendance, ssl=False)
                        sessions = await session_response.json()
                        if len(sessions) > 0:
                            has_attendance = True
                            break
        if has_attendance:
            break

    if has_other_modules:
        active_modules.append(1)
    else:
        no_active_modules.append(1)

    if has_attendance:
        with_attendance.append(1)
    else:
        no_attendance.append(1)



async def fetch_sikola_course():
    async with aiohttp.ClientSession() as session:
        active_semester = "TA241"
        data_reports = []
        backup_file = "backup_course_data_07-12.pkl"

        # Coba muat data dari backup
        backup_data = load_backup(backup_file)
        processed_prodi = set(backup_data["processed_prodi"]) if backup_data else set()
        data_reports = backup_data["data_reports"] if backup_data else []

        with open("data/prodi_semester.json", "r", encoding="utf-8") as faculty:
            datafakultasProdi = faculty.read()

        datafakultas = json.loads(datafakultasProdi)

        for prodi in datafakultas["prodis"]:
            nama_prodi = prodi["nama_resmi"]

            # Skip jika sudah diproses
            if nama_prodi in processed_prodi:
                continue

            fakultas = prodi["fakultas"]["nama_resmi"]

            # Request kategori berdasarkan prodi
            param_prodi = {
                "wsfunction": "core_course_get_categories",
                "criteria[0][key]": "name",
                "criteria[0][value]": nama_prodi,
            }
            response = await session.get(baseUrl, params=param_prodi, ssl=False)
            response = await response.json()

            if not response:
                continue

            param_prodi_courses = {
                "wsfunction": "core_course_get_courses_by_field",
                "field": "category",
                "value": response[0]["id"],
            }

            response = await session.get(baseUrl, params=param_prodi_courses, ssl=False)
            result_course = await response.json()

            filtered_courses = [
                course
                for course in result_course["courses"]
                if active_semester in course["shortname"]
            ]

            total_courses = len(filtered_courses)
            active_modules, no_active_modules = [], []
            with_attendance, no_attendance = [], []

            # Buat tasks untuk memproses courses secara paralel
            tasks = []
            for course in filtered_courses:
                tasks.append(
                    process_course(
                        session,
                        baseUrl,
                        course,
                        active_modules,
                        no_active_modules,
                        with_attendance,
                        no_attendance,
                    )
                )
                if len(tasks) % 100 == 0:  
                    await asyncio.gather(*tasks)
                    tasks = []

            # Eksekusi sisa tasks
            if tasks:
                await asyncio.gather(*tasks)

            # Calculate percentages
            attendance_percentage = (len(with_attendance) / total_courses * 100) if total_courses else 0
            active_percentage = (len(active_modules) / total_courses * 100) if total_courses else 0
            
            print(nama_prodi)
            # Tambahkan data ke laporan
            data_reports.append(
                [
                    nama_prodi,
                    fakultas,
                    total_courses,
                    len(no_active_modules),
                    len(active_modules),
                    len(no_attendance),
                    len(with_attendance),
                    attendance_percentage,
                    active_percentage,
                ]
            )

            # Tandai prodi sebagai selesai diproses
            processed_prodi.add(nama_prodi)

            # Simpan progres ke backup file
            save_backup(backup_file, {"processed_prodi": processed_prodi, "data_reports": data_reports})

        # Buat DataFrame dan simpan ke file Excel
        df = pd.DataFrame(
            data_reports,
            columns=[
                "Nama Prodi",
                "Nama Fakultas",
                "Jumlah Total Course",
                "Jumlah Tidak Aktif",
                "Jumlah Aktif",
                "Jumlah Tanpa Attendance",
                "Jumlah Dengan Attendance",
                "Persentase Attendance (%)",
                "Persentase Aktif (%)",
            ],
        )

        df.to_excel("course_reports_inovasi_07-Des.xlsx", index=False)

        # Hapus backup file setelah semua selesai
        if os.path.exists(backup_file):
            os.remove(backup_file)


if __name__ == "__main__":
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"
    asyncio.run(fetch_sikola_course())
