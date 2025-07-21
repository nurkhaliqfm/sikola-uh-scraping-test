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


def save_backup_list(
    backup_list, filename="log/backup_list_attendance_course-mahasiswa.pkl"
):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/backup_list_attendance_course-mahasiswa.pkl"):
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return None


backup_list = load_backup_list()

if backup_list is None:
    backup_list = list([])
    save_backup_list(backup_list)
else:
    print("Backup list loaded successfully.")

resultFetch = []
currentDate = "2024-19-07"

dataReports = []


async def course_reports(
    session, baseUrl, courseData, namaProdi, namaKelas, namaMatkul, idNumber, fakultas
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
        
        total_sections = 0
        total_modules = 0
        
        for section in dataCourseContent:
        # Jika nama section bukan "Info Matakuliah", lakukan perhitungan
            if section["name"] != "Info Matakuliah":
                total_sections += 1
                total_modules += len(section["modules"])

    # Tampilkan hasil perhitungan
        print(f"Jumlah section yang bukan 'Info Matakuliah': {total_sections} {course_id}")
        print(f"Total jumlah module di semua section yang valid: {total_modules}")

        
        
        paramsEnroll = {
            "wsfunction": "core_enrol_get_enrolled_users",
            "courseid": courseData["courses"][0]["id"],
        }

        responseUser = await session.get(
            baseUrl, params=paramsEnroll, ssl=False
        )

        dataUser = await responseUser.json()
        
        
        dosen_count = 0
        mahasiswa_count = 0

        for user in dataUser:
                if 'groups' in user:
                    for group in user['groups']:
                        # Cek nama grup apakah DOSEN atau MAHASISWA
                        if group['name'] == "DOSEN":
                            dosen_count += 1
                        elif group['name'] == "MAHASISWA":
                            mahasiswa_count += 1

            # Tampilkan hasil hitungan
        print(f"Jumlah DOSEN: {dosen_count}")
        print(f"Jumlah MAHASISWA: {mahasiswa_count}")
        
        
        print(f"Nama Kelas : {namaKelas}")
        
        
        dataReports.append([
            course_id, namaKelas, namaProdi, fakultas, dosen_count, mahasiswa_count, total_sections, total_modules
        ])

        
        
      
async def fetch_sikola_course():
    async with aiohttp.ClientSession() as session:
        task = []

        for filePath in listDataDetailKelasFile:
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
            
            fakultas = ""
            for prodi in datafakultas['prodis']:
                if prodi['nama_resmi'].startswith(nama_prodi):
                    fakultas = prodi['fakultas']['nama_resmi']
                    break

            if idnumber_sikola not in backup_list:
                paramsAPIGetCourseByField = {
                    "wsfunction": "core_course_get_courses_by_field",
                    "field": "idnumber",
                    "value": idnumber_sikola,
                }

                responseGetCourseSikolaByField = await session.get(
                    baseUrl, params=paramsAPIGetCourseByField, ssl=False
                )

                dataCourseSikola = await responseGetCourseSikolaByField.json()

                print(f"Progress: {nama_prodi} {nama_kelas}")
                task.append(
                    course_reports(
                        session,
                        baseUrl,
                        dataCourseSikola,
                        nama_prodi,
                        nama_kelas,
                        nama_matkul,
                        idnumber_sikola,
                        fakultas
                    )
                )

            if len(task) % 100 == 0:
                await asyncio.gather(*task)
                task = []
        if task:
            await asyncio.gather(*task)
        
        df = pd.DataFrame(dataReports, columns=[
            'courseid', 'NAMA KELAS', 'NAMA PRODI', "NAMA FAKULTAS", 'JUMLAH DOSEN', 'JUMLAH MAHASISWA', 'JUMLAH ALUR', 'JUMLAH AKTIFITAS'
        ])

        # Simpan DataFrame ke file Excel
        df.to_excel("course_reports.xlsx", index=False)
        # dataReports.to_excel("course_reports.xlsx", index=False)



if __name__ == "__main__":
    kelasActiveName = "TA232.12"
    listDataDetailKelasFile = glob.glob(f"data/detailkelas/{kelasActiveName}/*.json")
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"
    loopingSize = len(listDataDetailKelasFile)

    asyncio.run(fetch_sikola_course())