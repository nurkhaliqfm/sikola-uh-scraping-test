import aiohttp
import asyncio
import glob
import os
import requests
import json
import pickle
import pandas as pd
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
load_dotenv()

# Disable InsecureRequestWarning
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# def save_backup_list(
#     backup_list, filename="log/presensi-cek.pkl"
# ):
#     with open(filename, "wb") as file:
#         pickle.dump(backup_list, file)


# def load_backup_list(filename="log/presensi-cek.pkl"):
#     try:
#         with open(filename, "rb") as file:
#             return pickle.load(file)
#     except FileNotFoundError:
#         return None


# backup_list = load_backup_list()

# if backup_list is None:
#     backup_list = list([])
#     save_backup_list(backup_list)
# else:
#     print("Backup list loaded successfully.")

resultFetch = []

dataReports = []

def load_backup(backup_file):
    if os.path.exists(backup_file):
        with open(backup_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Fungsi untuk menyimpan backup ke file
def save_backup(backup_file, data):
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

async def fetch_sikola_course(kelasActiveName):
    backup_file = "deleteSessionPresensi-action.json"
    excel_file = "presensi_cek_20_02-Delete.xlsx"

    # Memuat data dari backup jika tersedia
    backup_data = load_backup(backup_file)
    dataReports = backup_data.get('dataReports', [])
    processed_courses = backup_data.get('processed_courses', [])

    async with aiohttp.ClientSession() as session:
        task = []
        currentFile = 0
        loopingSize = len(listDataDetailKelasFile)

        for filePath in listDataDetailKelasFile:
            currentFile += 1

            with open(filePath, "r", encoding="utf-8") as f:
                data = f.read()
            
            with open('data/listProdi.json', "r", encoding="utf-8") as faculty:
                datafakultasProdi = faculty.read()

            dataDetailCourse = json.loads(data)
            datafakultas = json.loads(datafakultasProdi)

            nama_prodi = dataDetailCourse["nama_prodi"]
            nama_kelas = dataDetailCourse["nama_kelas"]
            nama_matkul = dataDetailCourse["nama_matkul"]
            idnumber_sikola = dataDetailCourse["idnumber_sikola"]

            # Cek apakah course ini sudah diproses
            if idnumber_sikola in processed_courses:
                print(f"Course {idnumber_sikola} sudah ada di backup, lewati...")
                continue
            
            fakultas = ""
            for prodi in datafakultas['prodis']:
                if prodi['nama_resmi'].startswith(nama_prodi):
                    fakultas = prodi['fakultas']['nama_resmi']
                    break

            try:
                # Mendapatkan data course dari API
                paramsAPIGetCourseByField = {
                    "wsfunction": "core_course_get_courses_by_field",
                    "field": "idnumber",
                    "value": idnumber_sikola,
                }

                responseGetCourseSikolaByField = await session.get(
                    baseUrl, params=paramsAPIGetCourseByField, ssl=False
                )

                dataCourseSikola = await responseGetCourseSikolaByField.json()

                print(f"Progress: {((currentFile / loopingSize) * 100):.2f} % - Processing {nama_prodi} {nama_kelas}")
                
                # Panggil fungsi untuk memproses course dan attendance
                task.append(
                    course_reports(
                        session,
                        baseUrl,
                        dataCourseSikola,
                        nama_prodi,
                        nama_kelas,
                        nama_matkul,
                        idnumber_sikola,
                        fakultas,
                        dataReports,
                        dataDetailCourse,
                        kelasActiveName
                    )
                )
                processed_courses.append(idnumber_sikola)  # Tambahkan ke daftar course yang diproses
                
            except Exception as e:
                print(f"Error processing course {idnumber_sikola}: {str(e)}")
            
            # Simpan backup setiap 10 course yang diproses
            if len(processed_courses) % 10 == 0:
                save_backup(backup_file, {'dataReports': dataReports, 'processed_courses': processed_courses})

                # Simpan DataFrame ke file Excel
                df = pd.DataFrame(dataReports, columns=[
                    'courseid', 'NAMA KELAS', 'NAMA PRODI', "NAMA FAKULTAS", 'JUMLAH PRESENSI/SESSION', 'KETERANGAN PRESENSI', 'LINK PRESENSI SIKOLA', 'ID KELAS'
                ])
                df.to_excel(excel_file, index=False)

            # Jalankan task setiap 100 course
            if len(task) % 100 == 0:
                await asyncio.gather(*task)
                task = []

        if task:
            await asyncio.gather(*task)

        # Backup terakhir sebelum exit
        save_backup(backup_file, {'dataReports': dataReports, 'processed_courses': processed_courses})

        # Simpan DataFrame ke file Excel terakhir
        df = pd.DataFrame(dataReports, columns=[
            'courseid', 'NAMA KELAS', 'NAMA PRODI', "NAMA FAKULTAS", 'JUMLAH PRESENSI/SESSION', 'KETERANGAN PRESENSI', 'LINK PRESENSI SIKOLA/COURSE', 'ID KELAS'
        ])
        df.to_excel(excel_file, index=False)
async def course_reports(
    session, baseUrl, courseData, namaProdi, namaKelas, namaMatkul, idNumber, fakultas, dataReports, dataDetailCourse, kelasActiveName
):
    if courseData["courses"]:
        paramsAPIGetCourseContent = {
            "wsfunction": "core_course_get_contents",
            "courseid": courseData["courses"][0]["id"],
        }
        
        course_id = courseData["courses"][0]["id"]

        responseGetCourseContent = await session.get(
            baseUrl, params=paramsAPIGetCourseContent, ssl=False
        )

        dataCourseContent = await responseGetCourseContent.json()
        
        attendanceId = None
        sessionid = None
        attendanceUrl = None
        section_name = None
        
        kelas_id = idNumber.split('.')[1]

        # Cek apakah course punya module attendance
        for section in dataCourseContent:
            for module in section["modules"]:
                if module["modname"] == "attendance":
                    attendanceId = module["instance"]
                    section_name = section["name"]
                    attendanceUrl = module["url"]  
                    break
        
        # Jika module attendance ditemukan
        if attendanceId:
            paramsGetSession = {
                "wsfunction": "mod_attendance_get_sessions",
                "attendanceid": attendanceId,
            }
            
            responseSession = await session.get(
                baseUrl, params=paramsGetSession, ssl=False
            )

            dataSession = await responseSession.json()
            
            # Hitung jumlah session
            jumlahSession = len(dataSession)
            
            if dataSession and jumlahSession > 0 :
                for sessionPresensi in dataSession:
                    if sessionPresensi['groupid'] == 0:
                        
                        print(sessionPresensi['id'])
                        sessionid = sessionPresensi['id']

                        
                        paramsGetSession = {
                                "wsfunction": "mod_attendance_remove_session",
                                "sessionid": sessionPresensi['id'],
                        }
                        
                        responseSession = await session.post(
                            baseUrl, params=paramsGetSession, ssl=False
                        )

                        dataSession = await responseSession.json()
                        
                        print(dataSession)
                        
                    
            
                if sessionid:
                    
                    dataReports.append([
                        course_id,
                        namaKelas,
                        namaProdi,
                        fakultas,
                        attendanceUrl,
                        "Tidak Ada SESSION Presensi",  # Keterangan absence of attendance
                        f'https://sikola-v2.unhas.ac.id/course/view.php?id={course_id}',
                        kelas_id
                    ])
                    
                    os.makedirs(f"data/cekPresensi-session/{kelasActiveName}", exist_ok=True)

                    with open(f'data/cekPresensi-session/{kelasActiveName}/{kelas_id}.json', 'w', encoding='utf-8') as f:
                        json.dump(dataDetailCourse, f, ensure_ascii=False, indent=4)

                    
                    
                    
                else:
                    dataReports.append([
                        course_id,  
                        namaKelas, 
                        namaProdi,  
                        fakultas,   
                        jumlahSession,  
                        f"Session ID MHS DOSEN {section_name}",  
                        attendanceUrl,
                        kelas_id
                    ])
                 
            
            
          
            
            
          
            
            
            
            
        
        

if __name__ == "__main__":
    kelasActiveName = "TA242.5"
    listDataDetailKelasFile = glob.glob(f"data/cekPresensi-session/{kelasActiveName}/*.json")
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=4a91b2ebcb33cfb3f24d2678b2e214df&moodlewsrestformat=json"
    loopingSize = len(listDataDetailKelasFile)

    asyncio.run(fetch_sikola_course(kelasActiveName))