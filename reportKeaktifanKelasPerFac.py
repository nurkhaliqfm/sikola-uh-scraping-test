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


async def get_sync_status(session, course_id):
    """
    Mengambil status sinkronisasi nilai dari API.
    """
    url = f"https://sikola-v2.unhas.ac.id/grade/getSinkronRPS.php?courseId={course_id}"
    headers = {
        "Authorization": "Bearer ccd437b923b46aa49e922034903ac628a447f11f8cf4d464d7d21b790ccc6ab7e88a96fb5b4cee1a87ab1dddb3aea7e3a715ad9f0d9f730de09af7caa56b7a73044ef0a7be7fb15931152f0ecb66f78d1b202f1103d0820ccd445186896062f769a6818bbf1963a6790940b0059e47933637b60aecec366c7c62aebfce7f8e1f"  # Ganti dengan token otorisasi
    }
    async with session.get(url, headers=headers) as response:
        data = await response.json()
        if data['status']:
            return True 
        return False



async def process_course(session, baseUrl, course, active_modules, no_active_modules, with_attendance, no_attendance, with_rps, no_rps):
    courseid = course["id"]
    
    param_course = {
        "wsfunction": "core_course_get_contents",
        "courseid": courseid,
    }
    response = await session.get(baseUrl, params=param_course, ssl=False)
    contents = await response.json()

    has_attendance = False  # Default value for has_attendance

    has_other_modules = any(
        isinstance(section, dict) and 
        "section" in section and
        "modules" in section and
        isinstance(section["modules"], list) and 
        section["section"] != 0 and
        len(section["modules"]) > 0 and
        any(isinstance(mod, dict) and "modname" in mod for mod in section["modules"])  # Ensure mod is a dictionary and has modname
        for section in contents
    ) and len(contents) > 1
    
    is_sync = await get_sync_status(session, courseid)
    

    
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

    if is_sync:
        with_rps.append(1)
    else:
        no_rps.append(1)
        
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
        active_semester = "TA242"
        data_reports = []
        backup_file = "sinkronKeaktifan-TA242-23Jan.pkl"

        # Load backup data
        backup_data = load_backup(backup_file)
        processed_prodi = set(backup_data["processed_prodi"]) if backup_data else set()
        data_reports = backup_data["data_reports"] if backup_data else []

        with open("data/prodi_semester.json", "r", encoding="utf-8") as faculty_file:
            datafakultasProdi = json.load(faculty_file)

        fakultas_sheets = {}

        for prodi in datafakultasProdi["prodis"]:
            nama_prodi = prodi["nama_resmi"]

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

                    
            


            total_courses = len(filtered_courses)
            active_modules, no_active_modules = [], []
            with_attendance, no_attendance = [], []
            with_rps, no_rps = [], []

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
                        with_rps,
                        no_rps
                    )
                )
                if len(tasks) % 100 == 0:
                    await asyncio.gather(*tasks)
                    tasks = []

            if tasks:
                await asyncio.gather(*tasks)

            attendance_percentage = (len(with_attendance) / total_courses * 100) if total_courses else 0
            active_percentage = (len(active_modules) / total_courses * 100) if total_courses else 0
            rps_percentage = (len(with_rps) / total_courses * 100) if total_courses else 0
            print(nama_prodi)

            data_reports.append(
                [
                    nama_prodi,
                    fakultas,
                    total_courses,
                    len(no_active_modules),
                    len(active_modules),
                    len(no_attendance),
                    len(with_attendance),
                    len(with_rps),
                    len(no_rps),
                    attendance_percentage,
                    active_percentage,
                    rps_percentage
                ]
            )

            processed_prodi.add(nama_prodi)

            save_backup(backup_file, {"processed_prodi": processed_prodi, "data_reports": data_reports})

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
                "Jumlah Sinkron RPS",
                "Jumlah Tidak Sinkron RPS",
                "Persentase Attendance (%)",
                "Persentase Aktif (%)",
                "Persentase Sinkron RPS (%)",
            ],
        )

        grouped = df.groupby("Nama Fakultas")
        with pd.ExcelWriter("sinkronKeaktfian_16JUN-2.xlsx") as writer:
            for fakultas, group in grouped:
                group.loc["Total"] = group[[
                    "Jumlah Total Course",
                    "Jumlah Tidak Aktif",
                    "Jumlah Aktif",
                    "Jumlah Tanpa Attendance",
                    "Jumlah Dengan Attendance",
                    "Jumlah Sinkron RPS",
                    "Jumlah Tidak Sinkron RPS",
                ]].sum()
                group.loc["Total", "Persentase Attendance (%)"] = group.loc["Total", "Jumlah Dengan Attendance"] / group.loc["Total", "Jumlah Total Course"] * 100
                group.loc["Total", "Persentase Aktif (%)"] = group.loc["Total", "Jumlah Aktif"] / group.loc["Total", "Jumlah Total Course"] * 100
                group.loc["Total", "Persentase Sinkron RPS (%)"] = group.loc["Total", "Jumlah Sinkron RPS"] / group.loc["Total", "Jumlah Total Course"] * 100
                group.to_excel(writer, sheet_name=fakultas, index=False)

        if os.path.exists(backup_file):
            os.remove(backup_file)


if __name__ == "__main__":
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=3bdff39b5f62204b247c93e852caad8b&moodlewsrestformat=json"
    asyncio.run(fetch_sikola_course())
