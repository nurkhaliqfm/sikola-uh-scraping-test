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
# todaysDate = "2024-02-21"
# todaysDate = "2024-02-22"

OldsDate = []
OldsDate = ["2024-02-19"]
# OldsDate = ["2024-02-19", "2024-02-20"]
# OldsDate = ["2024-02-19", "2024-02-20", "2024-02-21"]


async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        # baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"

        listDataDetailKelasFile = glob.glob(
            f"data/attendanceRaw/{todaysDate}/mahasiswa/*.json"
        )

        with open("data/DataExternal/Dictionary_Mahasiswa.json", "r") as f:
            dataDictionary = f.read()

        dictionaryMahasiswa = json.loads(dataDictionary)

        loopingSize = len(listDataDetailKelasFile)
        currentFile = 0

        for filePath in listDataDetailKelasFile:
            currentFile += 1
            splitOldPathFileName = filePath.split("/")[4]

            pertemuanKe = 1
            if len(OldsDate) > 0:
                for oldD in OldsDate:
                    newFilePath = (
                        f"data/attendanceRaw/{oldD}/mahasiswa/{splitOldPathFileName}"
                    )

                    cekAksesFileNew = os.path.isfile(newFilePath)
                    if cekAksesFileNew:
                        pertemuanKe += 1

            with open(filePath, "r") as f:
                data = f.read()

            dataCourseAttendance = json.loads(data)

            if not len(dataCourseAttendance) == 0:
                idCourseSikola = dataCourseAttendance[0]["courseid"]
                studentsStatus = dataCourseAttendance[0]["attendance_log"]
                students = dataCourseAttendance[0]["users"]
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
                    presensiMahasiswa = []

                    if not len(students) == 0:
                        for student in students:
                            isStudentLog = False
                            selectedUserStatus = ""
                            for studentstatus in studentsStatus:
                                if studentstatus["studentid"] == student["id"]:
                                    isStudentLog = True
                                    selectedUserStatus = studentstatus["statusid"]
                                    break

                            paramsAPIGetUserSikolaByField = {
                                "wsfunction": "core_user_get_users_by_field",
                                "field": "id",
                                "values[0]": student["id"],
                            }

                            responseGetUserSikolaByField = await session.get(
                                baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
                            )

                            dataUserSikolaDosen = (
                                await responseGetUserSikolaByField.json()
                            )

                            if isStudentLog:
                                for status in statusAttendance:
                                    if str(status["id"]) == selectedUserStatus:
                                        dataPresensi = {
                                            "nim": dataUserSikolaDosen[0]["username"],
                                            "nama_mahasiswa": dataUserSikolaDosen[0][
                                                "lastname"
                                            ],
                                            "status": status["description"],
                                        }
                                        presensiMahasiswa.append(dataPresensi)
                                        break
                            else:
                                dataPresensi = {
                                    "id_mahasiswa": dictionaryMahasiswa[
                                        dataUserSikolaDosen[0]["username"]
                                    ],
                                    "nim": dataUserSikolaDosen[0]["username"],
                                    "nama_mahasiswa": dataUserSikolaDosen[0][
                                        "lastname"
                                    ],
                                    "status": "Absent",
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
