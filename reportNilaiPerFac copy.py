import aiohttp
import asyncio
import os
import json
import pickle
import pandas as pd
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
from urllib3.exceptions import InsecureRequestWarning
import requests
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


load_dotenv()

# Fungsi untuk autentikasi Google Sheets



def load_backup(file_name):
    if os.path.exists(file_name):
        with open(file_name, "rb") as f:
            return pickle.load(f)
    return None


# Fungsi untuk menyimpan progres ke file backup
def save_backup(file_name, data):
    with open(file_name, "wb") as f:
        pickle.dump(data, f)

def authenticate_google_sheets(credentials_file):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
    client = gspread.authorize(creds)
    return client

# Fungsi untuk menulis data ke Google Sheets
def write_to_google_sheets(spreadsheet_name, grouped_data):
    client = authenticate_google_sheets("credentials.json")
    
    # Buat spreadsheet baru jika belum ada
    try:
        spreadsheet = client.open(spreadsheet_name)
    except gspread.exceptions.SpreadsheetNotFound:
        spreadsheet = client.create(spreadsheet_name)

    # Bagikan akses agar dapat diakses publik atau oleh email tertentu (opsional)
    # spreadsheet.share('your-email@example.com', perm_type='user', role='writer')  # Ganti email Anda

    # Tulis setiap grup fakultas ke sheet terpisah
    for fakultas, group in grouped_data:
        sheet_name = fakultas[:50]  # Nama sheet maksimal 50 karakter
        try:
            sheet = spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            sheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=20)

        # Konversi DataFrame ke list (termasuk header)
        data = [group.columns.tolist()] + group.fillna('').values.tolist()
        sheet.update("A1", data)


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


    
# Fungsi utama
async def fetch_sikola_course():
    async with aiohttp.ClientSession() as session:
        active_semester = "TA241"
        data_reports = []
        backup_file = "backup_nilai-15-12TA241.pkl"

        # Load backup data
        backup_data = load_backup(backup_file)
        processed_prodi = set(backup_data["processed_prodi"]) if backup_data else set()
        data_reports = backup_data["data_reports"] if backup_data else []

        with open("data/prodi_semester.json", "r", encoding="utf-8") as faculty_file:
            datafakultasProdi = json.load(faculty_file)

        for prodi in datafakultasProdi["prodis"]:
            nama_prodi = prodi["nama_resmi"]
            if nama_prodi in processed_prodi:
                continue

            fakultas = prodi["fakultas"]["nama_resmi"]
            
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


            # Tambahkan hasil ke data_reports
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
                "Persentase Nilai (%)",
            ],
        )
        df["Persentase Nilai (%)"] = df["Persentase Nilai (%)"].round(2)

        grouped = df.groupby("Nama Fakultas")

        # Tulis data ke Google Spreadsheet
        write_to_google_sheets("Course Nilai by Fakultas", grouped)

        if os.path.exists(backup_file):
            os.remove(backup_file)

if __name__ == "__main__":
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"
    asyncio.run(fetch_sikola_course())
