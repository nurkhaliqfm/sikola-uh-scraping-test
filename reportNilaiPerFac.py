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


BASE_URL = "https://sikola-v2.unhas.ac.id"

async def get_sync_status(session, course_id):
    """
    Mengambil status sinkronisasi nilai dari API.
    """
    url = f"{BASE_URL}/grade/getSinkronNilai.php?courseId={course_id}"
    headers = {
        "Authorization": "Bearer ccd437b923b46aa49e922034903ac628a447f11f8cf4d464d7d21b790ccc6ab7e88a96fb5b4cee1a87ab1dddb3aea7e3a715ad9f0d9f730de09af7caa56b7a73044ef0a7be7fb15931152f0ecb66f78d1b202f1103d0820ccd445186896062f769a6818bbf1963a6790940b0059e47933637b60aecec366c7c62aebfce7f8e1f"  # Ganti dengan token otorisasi
    }
    async with session.get(url, headers=headers) as response:
        data = await response.json()
        if data and len(data) > 0 and "status" in data[0]:
            return data[0]["status"] == 1  # True jika sinkron
        return False


async def process_course(session, baseUrl, course, total_sync, total_not_sync):
    course_id = course["id"]
    is_sync = await get_sync_status(session, course_id)
    
    if is_sync:
        total_sync.append(1)
    else:
        total_not_sync.append(1)


    

async def fetch_sikola_course():
    async with aiohttp.ClientSession() as session:
        active_semester = "TA241"
        data_reports = []
        backup_file = "backup_nilai-21-janTA241.pkl"

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
                        detail_kelas_path = f"data/detailKelas/TA241.19/{id_kelas}.json"
                        if os.path.exists(detail_kelas_path):
                            with open(detail_kelas_path, "r", encoding="utf-8") as kelas_file:
                                isiKelas = json.load(kelas_file)
                                if isiKelas['id_kelas_kuliah_jenis'] == 1:
                                    filtered_courses.append(course)

                    
          

            total_courses = len(filtered_courses)
            total_sync, total_not_sync = [], []

            tasks = []
            for course in filtered_courses:
                tasks.append(
                    process_course(
                        session,
                        baseUrl,
                        course,
                        total_sync,
                        total_not_sync,
                       
                    )
                )
                if len(tasks) % 100 == 0:
                    await asyncio.gather(*tasks)
                    tasks = []

            if tasks:
                await asyncio.gather(*tasks)

            nilai_percentage = (len(total_sync) / total_courses * 100) if total_courses else 0
            print(nama_prodi)

            data_reports.append(
                [
                    nama_prodi,
                    fakultas,
                    total_courses,
                    len(total_sync),
                    len(total_not_sync),   
                    nilai_percentage,
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
                "Jumlah Kelas Sinkron Nilai",
                "Jumlah Tidak Sinkron Nilai",
                "Persentase Sinkron (%)",
            ],
        )
        
        df["Persentase Sinkron (%)"] = df["Persentase Sinkron (%)"].round(0)


        grouped = df.groupby("Nama Fakultas")
        with pd.ExcelWriter("sinkron_nilai_by_fakultas_TA241_23Jan.xlsx") as writer:
            for fakultas, group in grouped:
                group.loc["Total"] = group[[
                    "Jumlah Total Course",
                    "Jumlah Kelas Sinkron Nilai",
                    "Jumlah Tidak Sinkron Nilai",
                ]].sum()
                group.loc["Total", "Persentase Sinkron (%)"] = group.loc["Total", "Jumlah Kelas Sinkron Nilai"] / group.loc["Total", "Jumlah Total Course"] * 100
                group["Persentase Sinkron (%)"] = group["Persentase Sinkron (%)"].round(0)  # Membulatkan nilai di baris Total juga

                group.to_excel(writer, sheet_name=fakultas, index=False)
                workbook = writer.book
                worksheet = writer.sheets[fakultas]
                for col in worksheet.columns:
                    max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
                    worksheet.column_dimensions[col[0].column_letter].width = max(15, max_length)
                worksheet.freeze_panes = "A2"  # Freeze header row

        if os.path.exists(backup_file):
            os.remove(backup_file)


if __name__ == "__main__":
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=99bb1320ef22fc37619dd027659e8d94&moodlewsrestformat=json"
    asyncio.run(fetch_sikola_course())
