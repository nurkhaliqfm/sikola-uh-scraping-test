import aiohttp
import asyncio
import glob
import os
import requests
import json
import pickle
import csv

from datetime import datetime, timedelta

from dotenv import load_dotenv

load_dotenv()

# Disable InsecureRequestWarning
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


API_NEOSIA = os.getenv('API_NEOSIA')
TOKEN = os.getenv('TOKEN')


async def process_file(filePath, session, headers):
    splitOldPathFileName = filePath.split("/")[3]
    retries = 3
    result_not_match = []
    for attempt in range(retries):
        try:
            id_kelas = splitOldPathFileName.split("\\")[1].split(".")[0]
            response = await session.get(
                f"{API_NEOSIA}/admin_mkpk/pertemuan",
                headers=headers,
                json={
                        "filters": {
                            "id_kelas_kuliah": id_kelas,
                        }
                    },
                ssl=False
            )
            resNeosia = await response.json()
            pertemuans = resNeosia.get('pertemuans', [])
            pertemuan_ke = 1
            if len(pertemuans) == 0:
                pertemuan_ke = 1
            for pertemuan in pertemuans:
                if pertemuan.get('tanggal_rencana', '') == todaysDate:
                    pertemuan_ke = pertemuan.get('pertemuan_ke', 1)
                    print(pertemuan, id_kelas)
                    # print(len(pertemuans), pertemuan_ke, id_kelas, splitOldPathFileName)
                    
                    
                    with open(filePath, "r") as f:
                            data = f.read()

                    dataCourseAttendance = json.loads(data)

                    if not len(dataCourseAttendance) == 0:
                        attendanceData = []
                        for i in range(0, len(dataCourseAttendance)):
                            idCourseSikola = dataCourseAttendance[i]["courseid"]
                            lecturerStatus = dataCourseAttendance[i]["attendance_log"]
                            lecturers = dataCourseAttendance[i]["users"]
                            statusAttendance = dataCourseAttendance[i]["statuses"]

                            print(f"Processing: {filePath}")

                            if len(lecturerStatus) > 0:
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

                                        dataUserSikolaDosen = (
                                            await responseGetUserSikolaByField.json()
                                        )

                                        dataUserSikolaDosen[0]["username"].upper()
                                        idDosen = dictionaryDosen.get(
                                            dataUserSikolaDosen[0]["username"].upper(), None
                                        )

                                        if not idDosen is None:
                                            if isDosenLog:
                                                for status in statusAttendance:
                                                    if (
                                                        str(status["id"]) == selectedUserStatus
                                                        and status["description"] == "Present"
                                                    ):
                                                        dataPresensi = {
                                                     
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
                    

                                    data = {
                                        "nama_matakuliah": dataCourseSikola["courses"][0][
                                            "fullname"
                                        ],
                                        "pertemuan": {
                                            "tanggal_rencana": tanggalRencana,
                                            "id_kelas_kuliah": idKelasKuliah,
                                            "pertemuan_ke": pertemuan_ke,
                                            "tema": "",
                                            "pokok_bahasan": "",
                                            "keterangan": "",
                                        },
                                        "presensi": presensiDosens,
                                    }
                                    attendanceData.append(data)

                                    with open(
                                        f"data/absensi/{todaysDate}/dosen/{idKelasKuliah}.json",
                                        "w",
                                    ) as f:
                                        json.dump(attendanceData, f, indent=4)
                    break
                else:
                    print(f"NOT-MATCH {id_kelas}")
                    res1 = await session.get(
                        f"{API_NEOSIA}/admin_mkpk/dosen/input_nilai/kelas_kuliah/{id_kelas}",
                        headers=headers,
                        ssl=False
                    )
                    response_data = await res1.json()
                    
                    res2 = await session.get(
                        f"{API_NEOSIA}/admin_mkpk/prodi",
                        headers=headers,
                        ssl=False
                    ) 
                    response_fakultas_data = await res2.json()

                    id_prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['id']
                    nama_kelas = response_data['kelasKuliah']['nama']
                    prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['nama_resmi']
                    nama_fakultas = next((p['fakultas']['nama_resmi'] for p in response_fakultas_data['prodis'] if p['id'] == id_prodi), None)
                    result_not_match.append([todaysDate, id_kelas, nama_kelas, prodi, nama_fakultas])
                    break
            break
        except Exception as e:
            print(f"Error fetching data for id_kelas DOSEN =  {id_kelas}: {e}")
            if attempt == retries - 1:
                print(f"Failed to fetch data for id_kelas DOSEN = {id_kelas} after {retries} attempts")

    with open(f"data/absensi/{todaysDate}/ListJadwalBerubah-Dosen.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["tanggal_rencana", "id_kelas", 'nama_kelas', 'prodi', "nama_fakultas"])
        writer.writerows(result_not_match)



async def fetch_sikola_course_users():
    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Authorization": f"Bearer {TOKEN}"
    }
    async with aiohttp.ClientSession() as session:
        tasks = []
        listDataDetailKelasFile = glob.glob(
            f"data/attendanceRaw/{todaysDate}/dosen/*.json"
        )

        for filePath in listDataDetailKelasFile:
            tasks.append(process_file(filePath, session, headers))
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
    end_date = "2024-03-14"

    todaysDate = end_date
    OldsDate = generate_olds_date(start_date, end_date)

    with open("data/DataExternal/Dictionary_Dosen.json", "r") as f:
        dataDictionary = f.read()

    statusPresensiNeosia = {
        "Present": 1,
        "Late": 1,
        "Excused": 4,
        "Absent": 2,
        "Sick": 3,
    }
    dictionaryDosen = json.loads(dataDictionary)
    
    # print()
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"
    resultFetch = []


    asyncio.run(fetch_sikola_course_users())
