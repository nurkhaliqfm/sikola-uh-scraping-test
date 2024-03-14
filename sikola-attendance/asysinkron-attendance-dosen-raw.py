import aiohttp
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

resultFetch = []
<<<<<<< Updated upstream
currentDate = "2024-03-04"
=======
currentDate = "2024-03-13"
>>>>>>> Stashed changes

def save_backup_list(
    backup_list, filename=f"log/{currentDate}_attendance_dosen_raw.pkl"
):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)

def load_backup_list(filename=f"log/{currentDate}_attendance_dosen_raw.pkl"):
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


async def attendance_item_raw(session, baseUrl, courseData, idKelasKuliah):
    print(f"Get Data {courseData['courses'][0]['fullname']}...")
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
        dosenGroupId = 0
        for groups in dataCourseGroup:
            if groups["name"] == "DOSEN":
                dosenGroupId = groups["id"]
                break

        if not dosenGroupId == 0:
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
                        if module["name"] == "Presensi Pengampu Mata Kuliah":
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

                                # currentDateValue = datetime.strptime(
                                #     currentDate, "%Y-%m-%d"
                                # )
                                # convertedDateValue = datetime.strptime(
                                #     convertDate, "%Y-%m-%d"
                                # )

                                # if convertedDateValue > currentDateValue:
                                #     break

                                if (
                                    convertDate == currentDate
                                    and item["groupid"] == dosenGroupId
                                ):
                                    resultAttendanceRaw.append(item)
                        
<<<<<<< Updated upstream
                        if len(resultAttendanceRaw) > 0:
                            with open(
                                f"data/attendanceRaw/{currentDate}/dosen/{idKelasKuliah}.json",
                                "w",
                            ) as f:
                                json.dump(resultAttendanceRaw, f, indent=4)
=======
                            if len(resultAttendanceRaw) > 0:
                                os.makedirs(f"data/attendanceRaw/{currentDate}/dosen", exist_ok=True)

                                with open(
                                    f"data/attendanceRaw/{currentDate}/dosen/{idKelasKuliah}.json",
                                    "w",
                                ) as f:
                                    json.dump(resultAttendanceRaw, f, indent=4)
>>>>>>> Stashed changes

                            break
                    break
                
    print(f"{courseData['courses'][0]['fullname']} DONE..!!")
    backup_list.append(courseData["courses"][0]["idnumber"])
    save_backup_list(backup_list)

async def attendance_get_raw(filePath, session):
    with open(filePath, "r", encoding="utf-8") as f:
        data = f.read()

    dataDetailCourse = json.loads(data)

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
        courseIdNumber = dataCourseSikola["courses"][0]["idnumber"]
        idKelasKuliah = courseIdNumber.split(".")[1]

        if not os.path.exists(
            f"data/attendanceRaw/{currentDate}/mahasiswa/{idKelasKuliah}.json"
        ):
            await attendance_item_raw(
                session, baseUrl, dataCourseSikola, idKelasKuliah
            )

async def fetch_sikola_course():
    async with aiohttp.ClientSession() as session:
        tasks = []
        print(f"Processing Course")

        for filePath in listDataDetailKelasFile:
            tasks.append(attendance_get_raw(filePath, session))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    kelasActiveName = "TA232.11"
    listDataDetailKelasFile = glob.glob(f"data/detailkelas/{kelasActiveName}/*.json")
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"

    asyncio.run(fetch_sikola_course())