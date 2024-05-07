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
currentDate = "2024-05-03"


# async def run_tasks_in_batches(tasks, batch_size):
#     for i in range(0, len(tasks), batch_size):
#         batch = tasks[i : i + batch_size]
#         await asyncio.gather(*batch)


async def course_reports(
    session, baseUrl, courseData, namaProdi, namaKelas, namaMatkul, idNumber
):
    if courseData["courses"]:
        dataReports = []
        paramsAPIGetCourseContent = {
            "wsfunction": "core_course_get_contents",
            "courseid": courseData["courses"][0]["id"],
        }

        responseGetCourseContent = await session.get(
            baseUrl, params=paramsAPIGetCourseContent, ssl=False
        )

        dataCourseContent = await responseGetCourseContent.json()
        print(f"Nama Kelas : {namaKelas}")
        if len(dataCourseContent) > 1:
            print(f"Pertemuan 1 : {dataCourseContent[1]['name']}")
            print(f"Content : {dataCourseContent[1]['modules']}")
        if len(dataCourseContent) > 2:
            print(f"Pertemuan 2 : {dataCourseContent[2]['name']}")
            print(f"Content : {dataCourseContent[2]['modules']}")
        if len(dataCourseContent) > 3:
            print(f"Pertemuan 3 : {dataCourseContent[3]['name']}")
            print(f"Content : {dataCourseContent[3]['modules']}")
        if len(dataCourseContent) > 4:
            print(f"Pertemuan 4 : {dataCourseContent[4]['name']}")
            print(f"Content : {dataCourseContent[4]['modules']}")
        if len(dataCourseContent) > 5:
            print(f"Pertemuan 5 : {dataCourseContent[5]['name']}")
            print(f"Content : {dataCourseContent[5]['modules']}")
        if len(dataCourseContent) > 6:
            print(f"Pertemuan 6 : {dataCourseContent[6]['name']}")
            print(f"Content : {dataCourseContent[6]['modules']}")
        if len(dataCourseContent) > 7:
            print(f"Pertemuan 7 : {dataCourseContent[7]['name']}")
            print(f"Content : {dataCourseContent[7]['modules']}")
        if len(dataCourseContent) > 8:
            print(f"Pertemuan 8 : {dataCourseContent[8]['name']}")
            print(f"Content : {dataCourseContent[8]['modules']}")
        if len(dataCourseContent) > 9:
            print(f"Pertemuan 9 : {dataCourseContent[9]['name']}")
            print(f"Content : {dataCourseContent[9]['modules']}")
        if len(dataCourseContent) > 10:
            print(f"Pertemuan 10 : {dataCourseContent[10]['name']}")
            print(f"Content : {dataCourseContent[10]['modules']}")
        if len(dataCourseContent) > 11:
            print(f"Pertemuan 11 : {dataCourseContent[11]['name']}")
            print(f"Content : {dataCourseContent[11]['modules']}")
        if len(dataCourseContent) > 12:
            print(f"Pertemuan 12 : {dataCourseContent[12]['name']}")
            print(f"Content : {dataCourseContent[12]['modules']}")
        if len(dataCourseContent) > 13:
            print(f"Pertemuan 13 : {dataCourseContent[13]['name']}")
            print(f"Content : {dataCourseContent[13]['modules']}")
        if len(dataCourseContent) > 14:
            print(f"Pertemuan 14 : {dataCourseContent[14]['name']}")
            print(f"Content : {dataCourseContent[14]['modules']}")
        if len(dataCourseContent) > 15:
            print(f"Pertemuan 15 : {dataCourseContent[15]['name']}")
            print(f"Content : {dataCourseContent[15]['modules']}")
        if len(dataCourseContent) > 16:
            print(f"Pertemuan 16 : {dataCourseContent[16]['name']}")
            print(f"Content : {dataCourseContent[16]['modules']}")

        itemReports = []
        itemReports.append(namaProdi.strip())
        itemReports.append(namaMatkul.strip())
        itemReports.append(namaKelas.strip())
        if len(dataCourseContent) > 1:
            itemReports.append(dataCourseContent[1]["name"].strip())
            itemReports.append(len(dataCourseContent[1]["modules"]))
        else:
            itemReports.append("NOTFOUND")
            itemReports.append("NOTFOUND")

        if len(dataCourseContent) > 2:
            itemReports.append(dataCourseContent[2]["name"].strip())
            itemReports.append(len(dataCourseContent[2]["modules"]))
        else:
            itemReports.append("NOTFOUND")
            itemReports.append("NOTFOUND")
        if len(dataCourseContent) > 3:
            itemReports.append(dataCourseContent[3]["name"].strip())
            itemReports.append(len(dataCourseContent[3]["modules"]))
        else:
            itemReports.append("NOTFOUND")
            itemReports.append("NOTFOUND")
        if len(dataCourseContent) > 4:
            itemReports.append(dataCourseContent[4]["name"].strip())
            itemReports.append(len(dataCourseContent[4]["modules"]))
        else:
            itemReports.append("NOTFOUND")
            itemReports.append("NOTFOUND")
        if len(dataCourseContent) > 5:
            itemReports.append(dataCourseContent[5]["name"].strip())
            itemReports.append(len(dataCourseContent[5]["modules"]))
        else:
            itemReports.append("NOTFOUND")
            itemReports.append("NOTFOUND")
        if len(dataCourseContent) > 6:
            itemReports.append(dataCourseContent[6]["name"].strip())
            itemReports.append(len(dataCourseContent[6]["modules"]))
        else:
            itemReports.append("NOTFOUND")
            itemReports.append("NOTFOUND")
        if len(dataCourseContent) > 7:
            itemReports.append(dataCourseContent[7]["name"].strip())
            itemReports.append(len(dataCourseContent[7]["modules"]))
        else:
            itemReports.append("NOTFOUND")
            itemReports.append("NOTFOUND")
        if len(dataCourseContent) > 8:
            itemReports.append(dataCourseContent[8]["name"].strip())
            itemReports.append(len(dataCourseContent[8]["modules"]))
        else:
            itemReports.append("NOTFOUND")
            itemReports.append("NOTFOUND")
        if len(dataCourseContent) > 9:
            itemReports.append(dataCourseContent[9]["name"].strip())
            itemReports.append(len(dataCourseContent[9]["modules"]))
        else:
            itemReports.append("NOTFOUND")
            itemReports.append("NOTFOUND")
        if len(dataCourseContent) > 10:
            itemReports.append(dataCourseContent[10]["name"].strip())
            itemReports.append(len(dataCourseContent[10]["modules"]))
        else:
            itemReports.append("NOTFOUND")
            itemReports.append("NOTFOUND")
        if len(dataCourseContent) > 11:
            itemReports.append(dataCourseContent[11]["name"].strip())
            itemReports.append(len(dataCourseContent[11]["modules"]))
        else:
            itemReports.append("NOTFOUND")
            itemReports.append("NOTFOUND")
        if len(dataCourseContent) > 12:
            itemReports.append(dataCourseContent[12]["name"].strip())
            itemReports.append(len(dataCourseContent[12]["modules"]))
        else:
            itemReports.append("NOTFOUND")
            itemReports.append("NOTFOUND")
        if len(dataCourseContent) > 13:
            itemReports.append(dataCourseContent[13]["name"].strip())
            itemReports.append(len(dataCourseContent[13]["modules"]))
        else:
            itemReports.append("NOTFOUND")
            itemReports.append("NOTFOUND")
        if len(dataCourseContent) > 14:
            itemReports.append(dataCourseContent[14]["name"].strip())
            itemReports.append(len(dataCourseContent[14]["modules"]))
        else:
            itemReports.append("NOTFOUND")
            itemReports.append("NOTFOUND")
        if len(dataCourseContent) > 15:
            itemReports.append(dataCourseContent[15]["name"].strip())
            itemReports.append(len(dataCourseContent[15]["modules"]))
        else:
            itemReports.append("NOTFOUND")
            itemReports.append("NOTFOUND")
        if len(dataCourseContent) > 16:
            itemReports.append(dataCourseContent[16]["name"].strip())
            itemReports.append(len(dataCourseContent[16]["modules"]))
        else:
            itemReports.append("NOTFOUND")
            itemReports.append("NOTFOUND")

        dataReports.append(itemReports)
        df = pd.DataFrame(
            dataReports,
            columns=[
                "Program Studi",
                "Nama Matakuliah",
                "Nama Kelas",
                "Nama Pertemuan 1",
                "Jumlah Item Pertemuan 1",
                "Nama Pertemuan 2",
                "Jumlah Item Pertemuan 2",
                "Nama Pertemuan 3",
                "Jumlah Item Pertemuan 3",
                "Nama Pertemuan 4",
                "Jumlah Item Pertemuan 4",
                "Nama Pertemuan 5",
                "Jumlah Item Pertemuan 5",
                "Nama Pertemuan 6",
                "Jumlah Item Pertemuan 6",
                "Nama Pertemuan 7",
                "Jumlah Item Pertemuan 7",
                "Nama Pertemuan 8",
                "Jumlah Item Pertemuan 8",
                "Nama Pertemuan 9",
                "Jumlah Item Pertemuan 9",
                "Nama Pertemuan 10",
                "Jumlah Item Pertemuan 10",
                "Nama Pertemuan 11",
                "Jumlah Item Pertemuan 11",
                "Nama Pertemuan 12",
                "Jumlah Item Pertemuan 12",
                "Nama Pertemuan 13",
                "Jumlah Item Pertemuan 13",
                "Nama Pertemuan 14",
                "Jumlah Item Pertemuan 14",
                "Nama Pertemuan 15",
                "Jumlah Item Pertemuan 15",
                "Nama Pertemuan 16",
                "Jumlah Item Pertemuan 16",
            ],
        )
        df.to_csv(
            f"data/CourseReport/{idNumber}.csv", index=False, header=True, sep=";"
        )


async def fetch_sikola_course():
    async with aiohttp.ClientSession() as session:
        task = []

        for filePath in listDataDetailKelasFile:
            with open(filePath, "r",  encoding="utf-8") as f:
                data = f.read()

            dataDetailCourse = json.loads(data)

            nama_prodi = dataDetailCourse["nama_prodi"]
            nama_kelas = dataDetailCourse["nama_kelas"]
            nama_matkul = dataDetailCourse["nama_matkul"]
            idnumber_sikola = dataDetailCourse["idnumber_sikola"]

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
                
                os.makedirs(f"data/CourseReport", exist_ok=True)

                if not os.path.exists(f"data/CourseReport/{idnumber_sikola}.csv"):
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
                        )
                    )

            if len(task) % 100 == 0:
                await asyncio.gather(*task)
                task = []
        if task:
            await asyncio.gather(*task)


if __name__ == "__main__":
    kelasActiveName = "TA232.12"
    listDataDetailKelasFile = glob.glob(f"data/detailkelas/{kelasActiveName}/*.json")
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"
    loopingSize = len(listDataDetailKelasFile)

    asyncio.run(fetch_sikola_course())