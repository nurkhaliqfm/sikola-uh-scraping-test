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
currentDate = "2024-02-27"


# async def run_tasks_in_batches(tasks, batch_size):
#     for i in range(0, len(tasks), batch_size):
#         batch = tasks[i : i + batch_size]
#         await asyncio.gather(*batch)


async def course_reports(
    session, baseUrl, courseData, namaProdi, namaKelas, namaMatkul, idNumber
):
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
    print(f"Pertemuan 1 : {dataCourseContent[1]['name']}")
    print(f"Content : {dataCourseContent[1]['modules']}")
    print(f"Pertemuan 2 : {dataCourseContent[2]['name']}")
    print(f"Content : {dataCourseContent[2]['modules']}")

    itemReports = []
    itemReports.append(namaProdi.strip())
    itemReports.append(namaMatkul.strip())
    itemReports.append(namaKelas.strip())
    itemReports.append(dataCourseContent[1]["name"].strip())
    itemReports.append(len(dataCourseContent[1]["modules"]))
    itemReports.append(dataCourseContent[2]["name"].strip())
    itemReports.append(len(dataCourseContent[2]["modules"]))

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
        ],
    )
    df.to_csv(f"data/CourseReport/{idNumber}.csv", index=False, header=True, sep=";")


async def fetch_sikola_course():
    async with aiohttp.ClientSession() as session:
        task = []

        for filePath in listDataDetailKelasFile:
            with open(filePath, "r") as f:
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
    kelasActiveName = "TA232.7"
    listDataDetailKelasFile = glob.glob(f"data/detailkelas/{kelasActiveName}/*.json")
    baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
    loopingSize = len(listDataDetailKelasFile)

    asyncio.run(fetch_sikola_course())
