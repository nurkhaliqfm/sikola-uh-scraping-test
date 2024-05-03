import aiohttp
import http.client

import asyncio
import glob
import os
import requests
import json
import pickle
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

load_dotenv()

# Disable InsecureRequestWarning
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def save_backup_list(
    backup_list, filename="log/backup_list_parsing-dosen-attandance.pkl"
):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/backup_list_parsing-dosen-attandance.pkl"):
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return None


async def process_file(filePath, session):
    splitOldPathFileName = filePath.split("/")[3].split("-")[0]

    with open(filePath, "r", encoding="utf-8") as f:
        dataJson = f.read()

    dataCourseAttendance = json.loads(dataJson)
    sessDate = dataCourseAttendance[0]["sessdate"]
    end_date = (
        datetime.fromtimestamp(sessDate, timezone.utc) + timedelta(hours=8)
    ).strftime("%Y-%m-%d")

    todaysDate = end_date
    OldsDate = generate_olds_date(start_date, end_date)

    pertemuanKe = 0
    if len(OldsDate) > 0:
        for oldD in OldsDate:
            # newFilePath = f"data/attendanceRaw/{oldD}/dosen/{splitOldPathFileName}"
            newFilePath = f"data/absensi/{oldD}/{splitOldPathFileName}.json"

            cekAksesFileNew = os.path.isfile(newFilePath)
            if cekAksesFileNew:
                with open(newFilePath, "r", encoding="utf-8") as f:
                    dataPresensiInDate = f.read()

                dataPresensiInDateJson = json.loads(dataPresensiInDate)
                pertemuanKe += len(dataPresensiInDateJson)

    if not len(dataCourseAttendance) == 0:
        attendanceData = []
        print("dataCourseAttendance :", len(dataCourseAttendance))
        for i in range(0, len(dataCourseAttendance)):
            idCourseSikola = dataCourseAttendance[i]["courseid"]
            lecturerStatus = dataCourseAttendance[i]["attendance_log"]
            lecturers = dataCourseAttendance[i]["users"]
            statusAttendance = dataCourseAttendance[i]["statuses"]

            # print(f"Progress: {((currentFile / loopingSize) * 100):.2f} %")
            print(f"Processing: {filePath}")

            if len(lecturerStatus) > 0:
                pertemuanKe += 1

                if idCourseSikola not in backup_list:
                    print(f"Id Course Sikola : {idCourseSikola}")

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
                    presensiDosens = []

                    if not len(lecturers) == 0:
                        presensiDosens = []
                        for dosen in lecturers:
                            isDosenLog = False
                            selectedUserStatus = ""
                            for lectureStatus in lecturerStatus:
                                if lectureStatus["studentid"] == dosen["id"]:
                                    isDosenLog = True
                                    selectedUserStatus = lectureStatus["statusid"]
                                    break

                            paramsAPIGetUserSikolaByField = {
                                "wsfunction": "core_user_get_users_by_field",
                                "field": "id",
                                "values[0]": dosen["id"],
                            }

                            responseGetUserSikolaByField = await session.get(
                                baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
                            )

                            dataUserSikolaDosen =(await responseGetUserSikolaByField.json())

                            dataUserSikolaDosen[0]["username"].upper()
                            idDosen = dictionaryDosen.get(
                                dataUserSikolaDosen[0]["username"].upper(), None
                            )

                            if not idDosen is None:
                                if isDosenLog:
                                    for status in statusAttendance:
                                        if (str(status["id"]) == selectedUserStatus and status["description"] == "Present"):
                                            dataPresensi = {
                                                # "nim": dataUserSikolaDosen[0]["username"],
                                                # "nama_mahasiswa": dataUserSikolaDosen[0][
                                                #     "lastname"
                                                # ],
                                                "id_pertemuan": "",
                                                "id_dosen": dictionaryDosen[
                                                    dataUserSikolaDosen[0][
                                                        "username"
                                                    ].upper()
                                                ],
                                                "id_tipe_kehadiran": statusPresensiNeosia[
                                                    status["description"]
                                                ],
                                            }
                                            presensiDosens.append(dataPresensi)
                                            break
                                # else:
                                #     dataPresensi = {
                                #         # "nim": dataUserSikolaDosen[0]["username"],
                                #         # "nama_mahasiswa": dataUserSikolaDosen[0][
                                #         #     "lastname"
                                #         # ],
                                #         "id_pertemuan": "",
                                #         "id_dosen": dictionaryDosen[
                                #             dataUserSikolaDosen[0]["username"].upper()
                                #         ],
                                #         "id_tipe_kehadiran": statusPresensiNeosia["Absent"],
                                #     }
                                #     presensiDosens.append(dataPresensi)

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
                            "presensi": presensiDosens,
                        }
                        attendanceData.append(data)
                        os.makedirs(f"data/absensi/{todaysDate}/dosen/", exist_ok=True)
                        with open(
                            f"data/absensi/{todaysDate}/dosen/{idKelasKuliah}.json",
                            "w",
                        ) as f:
                            json.dump(attendanceData, f, indent=4)
                        
                        os.makedirs(f"data/revisiAbsensi/{todays}/dosen/", exist_ok= True)
                        with open(
                            f"data/revisiAbsensi/{todays}/dosen/{idKelasKuliah}-{tanggalRencana}.json",
                            "w",
                        ) as f:
                            json.dump(attendanceData, f, indent=4)
                        
                        


async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        tasks = []
        listDataDetailKelasFile = glob.glob(
            f"data/revisiAttendanceRaw/{todays}/dosen/*.json"
        )

        for filePath in listDataDetailKelasFile:
            tasks.append(process_file(filePath, session))
        await asyncio.gather(*tasks)
        
        

                
            


def generate_olds_date(startDate, endDate):
    listOldsDate = []

    startDateValue = datetime.strptime(startDate, "%Y-%m-%d")
    endDateValue = datetime.strptime(endDate, "%Y-%m-%d")

    while startDateValue < endDateValue:
        listOldsDate.append(startDateValue.strftime("%Y-%m-%d"))
        startDateValue += timedelta(days=1)

    return listOldsDate



if __name__ == "__main__":
    start_date = "2024-02-19"
    todays = "2024-05-03-kendala-1"

    with open("data/DataExternal/Dictionary_Dosen_3.json", "r") as f:
        dataDictionary = f.read()

    statusPresensiNeosia = {
        "Present": 1,
        "Late": 1,
        "Excused": 4,
        "Absent": 2,
        "Sick": 3,
    }
    dictionaryDosen = json.loads(dataDictionary)
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"
    resultFetch = []

    backup_list = load_backup_list()

    if backup_list is None:
        backup_list = list([])
        save_backup_list(backup_list)
    else:
        print("Backup list loaded successfully.")

    asyncio.run(fetch_sikola_course_users())
