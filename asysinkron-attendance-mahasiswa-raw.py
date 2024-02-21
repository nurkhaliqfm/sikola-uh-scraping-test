import aiohttp
import asyncio
import glob
import os
import requests
import json
import pickle
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

# Disable InsecureRequestWarning
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def save_backup_list(backup_list, filename="log/backup_list_attendance_course.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/backup_list_attendance_course.pkl"):
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


async def attendance_intgrare(session, baseUrl, courseData, idKelasKuliah):

    task = []
    resultAttendanceRaw = []
    paramsAPIGetCourseContent = {
        "wsfunction": "core_course_get_contents",
        "courseid": courseData["courses"][0]["id"],
    }

    responseGetCourseContent = await session.get(
        baseUrl, params=paramsAPIGetCourseContent, ssl=False
    )

    dataCourseContent = await responseGetCourseContent.json()

    paramsAPIGetCourseGroup = {
        "wsfunction": "core_group_get_course_groups",
        "courseid": courseData["courses"][0]["id"],
    }

    responseGETCourseGroup = await session.get(
        baseUrl, params=paramsAPIGetCourseGroup, ssl=False
    )

    dataCourseGroup = await responseGETCourseGroup.json()
    if not len(dataCourseGroup) == 0:
        mahasiswaGroupId = dataCourseGroup[1]["id"]
        for content in dataCourseContent:
            if content["name"] == "Info Matakuliah":
                for module in content["modules"]:
                    if module["name"] == "Presensi Mahasiswa":
                        attendanceId = module["instance"]

                        paramsAttendaceSession = {
                            "wsfunction": "mod_attendance_get_sessions",
                            "attendanceid": attendanceId,
                        }

                        responseAttendanceSessions = await session.get(
                            baseUrl, params=paramsAttendaceSession, ssl=False
                        )

                        dataSessionsAttendance = await responseAttendanceSessions.json()
                        for item in dataSessionsAttendance:
                            sessDate = item["sessdate"]
                            convertDate = datetime.utcfromtimestamp(sessDate).strftime(
                                "%Y-%m-%d"
                            )
                            if (
                                convertDate == todaysDate
                                and item["groupid"] == mahasiswaGroupId
                            ):
                                resultAttendanceRaw.append(item)
                                with open(
                                    f"data/attendanceRaw/{todaysDate}/mahasiswa/{idKelasKuliah}.json",
                                    "w",
                                ) as f:
                                    json.dump(resultAttendanceRaw, f, indent=4)

    return task


async def fetch_sikola_course():
    async with aiohttp.ClientSession() as session:
        kelasActiveName = "TA232.4"
        listDataDetailKelasFile = glob.glob(
            f"data/detailkelas/{kelasActiveName}/*.json"
        )
        # baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=5efd77a7277c9ef1dc42a29cb812b552&moodlewsrestformat=json"

        loopingSize = len(listDataDetailKelasFile)
        currentFile = 0

        for filePath in listDataDetailKelasFile:
            currentFile += 1
            with open(filePath, "r") as f:
                data = f.read()

            dataDetailCourse = json.loads(data)

            idnumber_sikola = dataDetailCourse["idnumber_sikola"]
            shortname_sikola = dataDetailCourse["shortname_sikola"]
            mahasiswas = dataDetailCourse["mahasiswas"]
            dosens = dataDetailCourse["dosens"]
            sizeUserInCourse = len(dataDetailCourse["mahasiswas"]) + len(
                dataDetailCourse["dosens"]
            )

            print(f"Progress: {((currentFile / loopingSize) * 100):.2f} %")

            if idnumber_sikola not in backup_list:
                print(f"Shortname Course : {shortname_sikola}")

                paramsAPIGetCourseByField = {
                    "wsfunction": "core_course_get_courses_by_field",
                    "field": "idnumber",
                    "value": idnumber_sikola,
                }

                responseGetCourseSikolaByField = await session.get(
                    baseUrl, params=paramsAPIGetCourseByField, ssl=False
                )

                dataCourseSikola = await responseGetCourseSikolaByField.json()
                courseIdNumber = dataCourseSikola["courses"][0]["idnumber"]
                idKelasKuliah = courseIdNumber.split(".")[1]

                if not os.path.exists(
                    f"data/attendanceRaw/{todaysDate}/mahasiswa/{idKelasKuliah}.json"
                ):

                    task = await attendance_intgrare(
                        session,
                        baseUrl,
                        dataCourseSikola,
                        idKelasKuliah,
                    )
                    respnsesTask = await asyncio.gather(*task)

                    for res in respnsesTask:
                        print(res)
                        resultFetch.append(await res.json())


# get fetch_sikola_course()
if __name__ == "__main__":
    asyncio.run(fetch_sikola_course())
