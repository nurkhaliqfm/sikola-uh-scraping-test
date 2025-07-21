import aiohttp
import asyncio
import glob
import os
import requests
import json
import pickle

from dotenv import load_dotenv

load_dotenv()

# Disable InsecureRequestWarning
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def save_backup_list(
    backup_list, filename="log/backup_list_enrol_mahasiswa-enrole-group-MAHASISWA-A.pkl"
):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/backup_list_enrol_mahasiswa-enrole-group-MAHASISWA-A.pkl"):
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

async def enroll_user_grup_mhs(session, students, baseUrl, courseData):
    tasks = []

    # Dapatkan daftar grup di course
    paramsAPIGetCourseGroup = {
        "wsfunction": "core_group_get_course_groups",
        "courseid": courseData["courses"][0]["id"],
    }

    responseGETCourseGroup = await session.get(
        baseUrl, params=paramsAPIGetCourseGroup, ssl=False
    )

    dataCourseGroup = await responseGETCourseGroup.json()

    if dataCourseGroup:
        print("Student...")
        # Cari grup dengan nama MAHASISWA
        mahasiswaGroup = next(
            (group for group in dataCourseGroup if group["name"] == "MAHASISWA"), None
        )
        
        if mahasiswaGroup:
            mahasiswaGroupId = mahasiswaGroup["id"]

            # Dapatkan daftar peserta yang sudah terdaftar di course
            getUserPeserta = {
                "wsfunction": "core_enrol_get_enrolled_users",
                "courseid": courseData["courses"][0]["id"],
            }

            responseGetPeserta = await session.get(
                baseUrl, params=getUserPeserta, ssl=False
            )

            dataPeserta = await responseGetPeserta.json()

            # Buat set untuk menyimpan nim peserta yang sudah di grup MAHASISWA
            enrolledNIMs = set()

            for peserta in dataPeserta:
                if 'groups' in peserta and any(group["name"] == "MAHASISWA" for group in peserta["groups"]):
                    enrolledNIMs.add(peserta["username"])

            # Loop hanya untuk siswa yang belum di-enroll ke grup MAHASISWA
            for student in students:
                if student["nim"].lower() not in enrolledNIMs:
                    print(f"Enroll student: {student['nama_mahasiswa']} to MAHASISWA group")
                    
                    # Dapatkan data pengguna berdasarkan nim
                    paramsAPIGetUserSikolaByField = {
                        "wsfunction": "core_user_get_users_by_field",
                        "field": "username",
                        "values[0]": student["nim"].lower(),
                    }

                    responseGetUserSikolaByField = await session.get(
                        baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
                    )

                    dataUserSikola = await responseGetUserSikolaByField.json()
                    
                    if dataUserSikola:
                        userId = dataUserSikola[0]["id"]

                        # Enroll student ke grup MAHASISWA
                        paramsAPIEnrollMahasiswaToGroup = {
                            "wsfunction": "core_group_add_group_members",
                            "members[0][groupid]": mahasiswaGroupId,
                            "members[0][userid]": userId,
                        }

                        tasks.append(
                            session.get(baseUrl, params=paramsAPIEnrollMahasiswaToGroup, ssl=False)
                        )

        print("Student Done...")

    return tasks

async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        kelasActiveName = "TA241.1"

        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"


        listDataDetailKelasFile = glob.glob(
            f"data/detailkelas/{kelasActiveName}/*.json"
        )
        loopingSize = len(listDataDetailKelasFile)
        currentFile = 0

        for filePath in listDataDetailKelasFile:
            currentFile += 1
            with open(filePath, "r", encoding="utf-8") as f:
                data = f.read()

            dataDetailCourse = json.loads(data)
            idnumber_sikola = dataDetailCourse["idnumber_sikola"]
            mahasiswas = dataDetailCourse["mahasiswas"]


            print(f"Progress: {((currentFile / loopingSize) * 100):.2f} %")

            if idnumber_sikola not in backup_list:
                print(f"Shortname Course : {idnumber_sikola}")

                paramsAPIGetCourseByField = {
                    "wsfunction": "core_course_get_courses_by_field",
                    "field": "idnumber",
                    "value": idnumber_sikola,
                }

                responseGetCourseSikolaByField = await session.get(
                    baseUrl, params=paramsAPIGetCourseByField, ssl=False
                )

                dataCourseSikola = await responseGetCourseSikolaByField.json()

                task = await enroll_user_grup_mhs(
                    session,
                    mahasiswas,
                    baseUrl,
                    dataCourseSikola,
                )
                respnsesTask = await asyncio.gather(*task)

                for res in respnsesTask:
                    resultFetch.append(await res.json())

            backup_list.append(idnumber_sikola)
            save_backup_list(backup_list)
            # break


# get fetch_sikola_course()
if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
