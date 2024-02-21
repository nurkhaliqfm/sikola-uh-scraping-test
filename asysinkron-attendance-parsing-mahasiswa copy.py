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
    backup_list, filename="log/backup_list_parsing-mahasiswa-attandance.pkl"
):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/backup_list_parsing-mahasiswa-attandance.pkl"):
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
# todaysDate = "2024-02-19"
todaysDate = "2024-02-20"


# async def reshape_attenddance_raw(session, baseUrl, courseData, students, statusAtt):
#     attendanceData = []

#     print("Course Attendance...")
#     courseIdNumber = courseData["courses"][0]["idnumber"]
#     idKelasKuliah = courseIdNumber.split(".")[1]
#     tanggalRencana = todaysDate
#     pertemuanKe = 1
#     mahasiswa = []

#     if not len(students) == 0:
#         itemMahasiswa = []
#         for student in students:
#             print(f"Student Id: {student['studentid']}")

#             paramsAPIGetUserSikolaByField = {
#                 "wsfunction": "core_user_get_users_by_field",
#                 "field": "id",
#                 "values[0]": student["studentid"],
#             }

#             responseGetUserSikolaByField = await session.get(
#                 baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
#             )

#             dataUserSikolaDosen = await responseGetUserSikolaByField.json()
#             itemMahasiswa.append(dataUserSikolaDosen[0]["username"])
#             itemMahasiswa.append(dataUserSikolaDosen[0]["firstname"])

#         attendanceData.append(idKelasKuliah)
#         mahasiswa.append(itemMahasiswa)
#         mahasiswa.append(itemMahasiswa)

#     return attendanceData


async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        # baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=5efd77a7277c9ef1dc42a29cb812b552&moodlewsrestformat=json"

        listDataDetailKelasFile = glob.glob(
            f"data/attendanceRaw/{todaysDate}/mahasiswa/*.json"
        )

        loopingSize = len(listDataDetailKelasFile)
        currentFile = 0

        for filePath in listDataDetailKelasFile:
            currentFile += 1
            with open(filePath, "r") as f:
                data = f.read()

            dataCourseAttendance = json.loads(data)

            if not len(dataCourseAttendance) == 0:
                idCourseSikola = dataCourseAttendance[0]["courseid"]
                students = dataCourseAttendance[0]["attendance_log"]
                statusAttendance = dataCourseAttendance[0]["statuses"]

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

                            dataUserSikolaDosen = (
                                await responseGetUserSikolaByField.json()
                            )

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
                            "nama_matakuliah": dataCourseSikola["courses"][0][
                                "fullname"
                            ],
                            "id_kelas_kuliah": idKelasKuliah,
                            "tanggal_rencana": tanggalRencana,
                            "pertemuan_ke": pertemuanKe,
                            "presensi": presensiMahasiswa,
                        }
                        attendanceData.append(data)

                        with open(
                            f"data/absensi/{todaysDate}/mahasiswa/{idKelasKuliah}.json",
                            "w",
                        ) as f:
                            json.dump(attendanceData, f, indent=4)

        # for itemCourse in logCourseChange:
        #     currentFile += 1


# get fetch_sikola_course()
if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
