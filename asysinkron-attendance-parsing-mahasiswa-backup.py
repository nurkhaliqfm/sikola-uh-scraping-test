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


async def process_file(filePath, session):
    splitOldPathFileName = filePath.split("/")[4]

    pertemuanKe = 1
    if len(OldsDate) > 0:
        for oldD in OldsDate:
            newFilePath = f"data/attendanceRaw/{oldD}/mahasiswa/{splitOldPathFileName}"

            cekAksesFileNew = os.path.isfile(newFilePath)
            if cekAksesFileNew:
                pertemuanKe += 1

    with open(filePath, "r") as f:
        data = f.read()

    dataCourseAttendance = json.loads(data)

    if not len(dataCourseAttendance) == 0:
        # if dataCourseAttendance[0]["courseid"] == 44338:
        idCourseSikola = dataCourseAttendance[0]["courseid"]
        studentsStatus = dataCourseAttendance[0]["attendance_log"]
        students = dataCourseAttendance[0]["users"]
        statusAttendance = dataCourseAttendance[0]["statuses"]

        # print(f"Progress: {((currentFile / loopingSize) * 100):.2f} %")
        print(f"Processing: {filePath}")

        if len(studentsStatus) > 0:
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
                    presensiMahasiswa = []
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

                        dataUserSikolaDosen = await responseGetUserSikolaByField.json()

                        dataUserSikolaDosen[0]["username"].upper()
                        idMahasiswa = dictionaryMahasiswa.get(
                            dataUserSikolaDosen[0]["username"].upper(), None
                        )

                        if not idMahasiswa is None:
                            if isStudentLog:
                                for status in statusAttendance:
                                    if str(status["id"]) == selectedUserStatus:
                                        dataPresensi = {
                                            # "nim": dataUserSikolaDosen[0]["username"],
                                            # "nama_mahasiswa": dataUserSikolaDosen[0][
                                            #     "lastname"
                                            # ],
                                            "id_pertemuan": "",
                                            "id_mahasiswa": dictionaryMahasiswa[
                                                dataUserSikolaDosen[0][
                                                    "username"
                                                ].upper()
                                            ],
                                            "id_tipe_kehadiran": statusPresensiNeosia[
                                                status["description"]
                                            ],
                                        }
                                        presensiMahasiswa.append(dataPresensi)
                                        break
                            else:
                                dataPresensi = {
                                    # "nim": dataUserSikolaDosen[0]["username"],
                                    # "nama_mahasiswa": dataUserSikolaDosen[0][
                                    #     "lastname"
                                    # ],
                                    "id_pertemuan": "",
                                    "id_mahasiswa": dictionaryMahasiswa[
                                        dataUserSikolaDosen[0]["username"].upper()
                                    ],
                                    "id_tipe_kehadiran": statusPresensiNeosia["Absent"],
                                }
                                presensiMahasiswa.append(dataPresensi)

                    data = {
                        "nama_matakuliah": dataCourseSikola["courses"][0]["fullname"],
                        "pertemuan": {
                            "tanggal_rencana": tanggalRencana,
                            "id_kelas_kuliah": idKelasKuliah,
                            "pertemuan_ke": pertemuanKe,
                            "tema": "",
                            "pokok_bahasan": "",
                            "keterangan": "",
                        },
                        "presensi": presensiMahasiswa,
                    }
                    attendanceData.append(data)

                    with open(
                        f"data/absensi/{todaysDate}/mahasiswa/{idKelasKuliah}.json",
                        "w",
                    ) as f:
                        json.dump(attendanceData, f, indent=4)


async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        tasks = []
        # baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")

        listDataDetailKelasFile = glob.glob(
            f"data/attendanceRaw/{todaysDate}/mahasiswa/*.json"
        )

        # loopingSize = len(listDataDetailKelasFile)
        # currentFile = 0

        for filePath in listDataDetailKelasFile:
            # currentFile += 1
            tasks.append(process_file(filePath, session))
        await asyncio.gather(*tasks)


# get fetch_sikola_course()
if __name__ == "__main__":
    with open("data/DataExternal/Dictionary_Mahasiswa.json", "r") as f:
        dataDictionary = f.read()

    statusPresensiNeosia = {
        "Present": 1,
        "Late": 1,
        "Excused": 4,
        "Absent": 2,
        "Sick": 3,
    }
    dictionaryMahasiswa = json.loads(dataDictionary)
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"
    resultFetch = []

    # todaysDate = "2024-02-19"
    # OldsDate = []

    # todaysDate = "2024-02-20"
    # OldsDate = ["2024-02-19"]

    # todaysDate = "2024-02-21"
    # OldsDate = ["2024-02-19", "2024-02-20"]

    # todaysDate = "2024-02-22"
    # OldsDate = ["2024-02-19", "2024-02-20", "2024-02-21"]

    # todaysDate = "2024-02-23"
    # OldsDate = ["2024-02-19", "2024-02-20", "2024-02-21", "2024-02-22"]

    # todaysDate = "2024-02-24"
    # OldsDate = [
    #     "2024-02-19",
    #     "2024-02-20",
    #     "2024-02-21",
    #     "2024-02-22",
    #     "2024-02-23",
    # ]

    # todaysDate = "2024-02-25"
    # OldsDate = [
    #     "2024-02-19",
    #     "2024-02-20",
    #     "2024-02-21",
    #     "2024-02-22",
    #     "2024-02-23",
    #     "2024-02-24",
    # ]

    # todaysDate = "2024-02-26"
    # OldsDate = [
    #     "2024-02-19",
    #     "2024-02-20",
    #     "2024-02-21",
    #     "2024-02-22",
    #     "2024-02-23",
    #     "2024-02-24",
    #     "2024-02-25",
    # ]

    # todaysDate = "2024-02-27"
    # OldsDate = [
    #     "2024-02-19",
    #     "2024-02-20",
    #     "2024-02-21",
    #     "2024-02-22",
    #     "2024-02-23",
    #     "2024-02-24",
    #     "2024-02-25",
    #     "2024-02-26",
    # ]

    # todaysDate = "2024-02-28"
    # OldsDate = [
    #     "2024-02-19",
    #     "2024-02-20",
    #     "2024-02-21",
    #     "2024-02-22",
    #     "2024-02-23",
    #     "2024-02-24",
    #     "2024-02-25",
    #     "2024-02-26",
    #     "2024-02-27",
    # ]

    # todaysDate = "2024-02-29"
    # OldsDate = [
    #     "2024-02-19",
    #     "2024-02-20",
    #     "2024-02-21",
    #     "2024-02-22",
    #     "2024-02-23",
    #     "2024-02-24",
    #     "2024-02-25",
    #     "2024-02-26",
    #     "2024-02-27",
    #     "2024-02-28",
    # ]

    # todaysDate = "2024-03-01"
    # OldsDate = [
    #     "2024-02-19",
    #     "2024-02-20",
    #     "2024-02-21",
    #     "2024-02-22",
    #     "2024-02-23",
    #     "2024-02-24",
    #     "2024-02-25",
    #     "2024-02-26",
    #     "2024-02-27",
    #     "2024-02-28",
    #     "2024-02-29",
    # ]

    # todaysDate = "2024-03-02"
    # OldsDate = [
    #     "2024-02-19",
    #     "2024-02-20",
    #     "2024-02-21",
    #     "2024-02-22",
    #     "2024-02-23",
    #     "2024-02-24",
    #     "2024-02-25",
    #     "2024-02-26",
    #     "2024-02-27",
    #     "2024-02-28",
    #     "2024-02-29",
    #     "2024-03-01",
    # ]

    # todaysDate = "2024-03-03"
    # OldsDate = [
    #     "2024-02-19",
    #     "2024-02-20",
    #     "2024-02-21",
    #     "2024-02-22",
    #     "2024-02-23",
    #     "2024-02-24",
    #     "2024-02-25",
    #     "2024-02-26",
    #     "2024-02-27",
    #     "2024-02-28",
    #     "2024-02-29",
    #     "2024-03-02",
    # ]

    # todaysDate = "2024-03-04"
    # OldsDate = [
    #     "2024-02-19",
    #     "2024-02-20",
    #     "2024-02-21",
    #     "2024-02-22",
    #     "2024-02-23",
    #     "2024-02-24",
    #     "2024-02-25",
    #     "2024-02-26",
    #     "2024-02-27",
    #     "2024-02-28",
    #     "2024-02-29",
    #     "2024-03-02",
    #     "2024-03-03",
    # ]

    todaysDate = "2024-03-05"
    OldsDate = [
        "2024-02-19",
        "2024-02-20",
        "2024-02-21",
        "2024-02-22",
        "2024-02-23",
        "2024-02-24",
        "2024-02-25",
        "2024-02-26",
        "2024-02-27",
        "2024-02-28",
        "2024-02-29",
        "2024-03-02",
        "2024-03-03",
        "2024-03-04",
    ]

    backup_list = load_backup_list()

    if backup_list is None:
        backup_list = list([])
        save_backup_list(backup_list)
    else:
        print("Backup list loaded successfully.")

    asyncio.run(fetch_sikola_course_users())
