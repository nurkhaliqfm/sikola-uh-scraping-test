import aiohttp
import asyncio
import glob
import os
import requests
import json
import pickle
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
# currentDate = "2024-02-19"
# currentDate = "2024-02-20"
# currentDate = "2024-02-21"
# currentDate = "2024-02-22"
# currentDate = "2024-02-23"
# currentDate = "2024-02-24"
# currentDate = "2024-02-25"
# currentDate = "2024-02-26"
# currentDate = "2024-02-27"
# currentDate = "2024-02-28"
# currentDate = "2024-02-29"
# currentDate = "2024-03-01"
# currentDate = "2024-03-02"
# currentDate = "2024-03-03"
# currentDate = "2024-03-04"
# currentDate = "2024-03-05"
# currentDate = "2024-03-06"
currentDate = "2024-03-07"


async def attendance_intgrare(session, baseUrl, courseData, idKelasKuliah):
    task = []
    resultAttendanceRaw = []

    paramsAPIGetCourseGroup = {
        "wsfunction": "core_group_get_course_groups",
        "courseid": courseData["courses"][0]["id"],
    }

    responseGETCourseGroup = await session.get(
        baseUrl, params=paramsAPIGetCourseGroup, ssl=False
    )

    dataCourseGroup = await responseGETCourseGroup.json()
    if not len(dataCourseGroup) == 0:
        mahasiswaGroupId = 0
        for groups in dataCourseGroup:
            if groups["name"] == "MAHASISWA":
                mahasiswaGroupId = groups["id"]
                break

        if not mahasiswaGroupId == 0:
            paramsAPIGetCourseContent = {
                "wsfunction": "core_course_get_contents",
                "courseid": courseData["courses"][0]["id"],
            }

            responseGetCourseContent = await session.get(
                baseUrl, params=paramsAPIGetCourseContent, ssl=False
            )

            dataCourseContent = await responseGetCourseContent.json()
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

                            dataSessionsAttendance = (
                                await responseAttendanceSessions.json()
                            )

                            for item in dataSessionsAttendance:
                                sessDate = item["sessdate"]
                                convertDate = (
                                    datetime.fromtimestamp(sessDate, timezone.utc)
                                    + timedelta(hours=8)
                                ).strftime("%Y-%m-%d")

                                currentDateValue = datetime.strptime(
                                    currentDate, "%Y-%m-%d"
                                )
                                convertedDateValue = datetime.strptime(
                                    convertDate, "%Y-%m-%d"
                                )

                                if convertedDateValue > currentDateValue:
                                    break

                                if (
                                    convertDate == currentDate
                                    and item["groupid"] == mahasiswaGroupId
                                ):
                                    resultAttendanceRaw.append(item)

                                    with open(
                                        f"data/attendanceRaw/{currentDate}/mahasiswa/{idKelasKuliah}.json",
                                        "w",
                                    ) as f:
                                        json.dump(resultAttendanceRaw, f, indent=4)

                            break
                    break
    return task


async def fetch_sikola_course():
    async with aiohttp.ClientSession() as session:
        loopingSize = len(listDataDetailKelasFile)
        currentFile = 0

        for filePath in listDataDetailKelasFile:
            currentFile += 1
            with open(filePath, "r") as f:
                data = f.read()

            dataDetailCourse = json.loads(data)

            idnumber_sikola = dataDetailCourse["idnumber_sikola"]
            shortname_sikola = dataDetailCourse["shortname_sikola"]

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
                    f"data/attendanceRaw/{currentDate}/mahasiswa/{idKelasKuliah}.json"
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


if __name__ == "__main__":
    kelasActiveName = "TA232.11"
    listDataDetailKelasFile = glob.glob(f"data/detailkelas/{kelasActiveName}/*.json")
    baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")

    asyncio.run(fetch_sikola_course())
