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


def save_backup_list(backup_list, filename="log/backup_list_enrol_dosen-enrole.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/backup_list_enrol_dosen-enrole.pkl"):
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
todaysDate = "2024-02-19"


async def reshape_attenddance_raw(session, baseUrl, courseData, students, statusAtt):
    attendanceData = []

    print("Course Attendance...")
    courseIdNumber = courseData["courses"][0]["idnumber"]
    idKelasKuliah = courseIdNumber.split(".")[1]
    tanggalRencana = todaysDate
    pertemuanKe = 1
    mahasiswa = []

    if not len(students) == 0:
        itemMahasiswa = []
        for student in students:
            print(f"Student Id: {student['studentid']}")

            paramsAPIGetUserSikolaByField = {
                "wsfunction": "core_user_get_users_by_field",
                "field": "id",
                "values[0]": student["studentid"],
            }

            responseGetUserSikolaByField = await session.get(
                baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
            )

            dataUserSikolaDosen = await responseGetUserSikolaByField.json()
            itemMahasiswa.append(dataUserSikolaDosen[0]["username"])
            itemMahasiswa.append(dataUserSikolaDosen[0]["firstname"])

        attendanceData.append(idKelasKuliah)
        mahasiswa.append(itemMahasiswa)
        mahasiswa.append(itemMahasiswa)

    return attendanceData


async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        barearToken = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImVjMTFmYjlkNWMyMzYyNDE3Yzk0MmM4YWEzMWFhMWU3M2YxMGY0OTQ5MmU3ZjY5NTcxOGZmMzUyZjI4MGVhMjc1ODZiY2FiMzVmYWFiMzMwIn0.eyJhdWQiOiIyIiwianRpIjoiZWMxMWZiOWQ1YzIzNjI0MTdjOTQyYzhhYTMxYWExZTczZjEwZjQ5NDkyZTdmNjk1NzE4ZmYzNTJmMjgwZWEyNzU4NmJjYWIzNWZhYWIzMzAiLCJpYXQiOjE3MDg0NDU3OTEsIm5iZiI6MTcwODQ0NTc5MSwiZXhwIjoxNzA4ODc3NzkxLCJzdWIiOiI4NTQ5NiIsInNjb3BlcyI6WyIqIl19.EbLYwOhbf2aSBY_X03XmNR3lLLbcBB4xa8VwINsRa4JbfKWH5-ni0mE3HYRotZwMGLSeUIlVOkdyjywQ_O7vUXSyEcQtBGdBbDDQ6LwNuqeoppWD1dcDe7Ppk6_5MG8razYtypcYTPYJH__RCsz1CRlBYYkh9tH_4gAORMLlE1VXTk7fyLg6OpysJndA46C5a7427LefXAOurJwGXfIRBdxSEU2WxSEw75wWo315PEqjgSHlik9RIUpPkO4q7jifMqmyJvtPcpr30s4ky7zAvDLZ5KZEoa3WPSRfdS0pC2GOYGQy1zm5OgbP05iAzmnVdNb5oLoRsdSqV5C1idHUTsSUveBNlR6GU5b9EOGziIbQvhMs7TF3onJqukvrxxl70hHe28RInOy5UoKMRo1u9WRe66nVqHA8IDaMfVkQ2KQa7tYxBodlXyzi_w2OwcX5ylukgie0sdtXQsrttePiQNiQszBcDsRMTrAiCzQc1pd7ojge5cJeHN5xG-r0DRfnfHi0iKYgJnJvpOvkXOZADmUjCTPrxnNXMcrF1j8AOrWE_GFLiEfABQLW8JdIVI3PsKUpAQRtAK5ENWwoIHiZtCY6c3ZvqFv5gYmmUCsmNapq-sBb4kTd1VKsErEQFmFKOJ1PjTjFHCyRz5lWd8lE9sZPxp11H6PR3Xq0XeEyhgY"
        baseUrl = "https://api.neosia.unhas.ac.id/api"

        listDataAbsensiKelas = glob.glob(f"data/detailkelas/{kelasActiveName}/*.json")

        logCourseChange = json.loads(dataChangeFile)

        loopingSize = len(logCourseChange)
        currentFile = 0

        for itemCourse in logCourseChange:
            currentFile += 1
            idCourseSikola = itemCourse["courseid"]
            students = itemCourse["attendance_log"]
            statusAttendance = itemCourse["statuses"]

            print(f"Progress: {((currentFile / loopingSize) * 100):.2f} %")

            if idCourseSikola not in backup_list:
                print(f"Id Course Sikola : {idCourseSikola}")
                attendanceData = []

                paramsAPIGetCourseByField = {
                    "wsfunction": "core_course_get_courses_by_field",
                    "field": "id",
                    "value": idCourseSikola,
                }

                responseGetCourseSikolaByField = await session.get(
                    baseUrl, params=paramsAPIGetCourseByField, ssl=False
                )

                dataCourseSikola = await responseGetCourseSikolaByField.json()

                print("Course Attendance...")
                courseIdNumber = dataCourseSikola["courses"][0]["idnumber"]
                idKelasKuliah = courseIdNumber.split(".")[1]
                tanggalRencana = todaysDate
                pertemuanKe = 1
                presensiMahasiswa = []

                if not len(students) == 0:
                    for student in students:

                        paramsAPIGetUserSikolaByField = {
                            "wsfunction": "core_user_get_users_by_field",
                            "field": "id",
                            "values[0]": student["studentid"],
                        }

                        responseGetUserSikolaByField = await session.get(
                            baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
                        )

                        dataUserSikolaDosen = await responseGetUserSikolaByField.json()

                        for status in statusAttendance:
                            if str(status["id"]) == student["statusid"]:
                                dataPresensi = {
                                    "nim": dataUserSikolaDosen[0]["username"],
                                    "nama_mahasiswa": dataUserSikolaDosen[0][
                                        "firstname"
                                    ],
                                    "status": status["description"],
                                }
                                presensiMahasiswa.append(dataPresensi)

                    data = {
                        "nama_matakuliah": dataCourseSikola["courses"][0]["fullname"],
                        "id_kelas_kuliah": idKelasKuliah,
                        "tanggal_rencana": tanggalRencana,
                        "pertemuan_ke": pertemuanKe,
                        "presensi": presensiMahasiswa,
                    }
                    attendanceData.append(data)

                    with open(
                        f"data/absensi/{todaysDate}/{idKelasKuliah}.json", "w"
                    ) as f:
                        json.dump(attendanceData, f, indent=4)


# get fetch_sikola_course()
if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
