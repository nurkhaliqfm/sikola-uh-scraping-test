import aiohttp
import asyncio
import glob
import os
import requests
import json
import pickle
import csv
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

load_dotenv()

# Disable InsecureRequestWarning
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

resultFetch = []
currentDate = "2024-03-07"

def save_backup_list(
    backup_list, filename=f"log/{currentDate}_revisi_attendance_dosen_raw.pkl"
):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename=f"log/{currentDate}_revisi_attendance_dosen_raw.pkl"):
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

async def attendance_item_raw(session, baseUrl, courseData, idKelasKuliah, classDate):
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
                                
                                
                                classDateConverted = datetime.strptime(classDate, "%d/%m/%Y").strftime("%Y-%m-%d")


                                # currentDateValue = datetime.strptime(
                                #     classDate, "%Y-%m-%d"
                                # )
                                # convertedDateValue = datetime.strptime(
                                #     convertDate, "%Y-%m-%d"
                                # )

                                # if convertedDateValue > currentDateValue:
                                #     break

                                if (
                                    convertDate == classDateConverted
                                    and item["groupid"] == dosenGroupId
                                ):
                                    resultAttendanceRaw.append(item)

                            if len(resultAttendanceRaw) > 0:
                                with open(
                                    f"data/attendanceRaw/{classDateConverted}/dosen/{idKelasKuliah}.json",
                                    "w",
                                ) as f:
                                    json.dump(resultAttendanceRaw, f, indent=4)
                                with open(
                                    f"data/revisiAttendanceRaw/{currentDate}/dosen/{idKelasKuliah}-{classDateConverted}.json",
                                    "w",
                                ) as f:
                                    json.dump(resultAttendanceRaw, f, indent=4)

                            break
                    break
                
    print(f"{courseData["courses"][0]["fullname"]} DONE..!!")
    # backup_list.append(courseData["courses"][0]["shortname"])
    # save_backup_list(backup_list)


async def attendance_get_raw(session, itemClassError):
    if not itemClassError[0] == "fullname_kelas_sikola":
        shortname_sikola = f"TA232-{itemClassError[1]}"
        if shortname_sikola not in backup_list:
            paramsAPIGetCourseByField = {
                "wsfunction": "core_course_get_courses_by_field",
                "field": "shortname",
                "value": shortname_sikola,
            }

            responseGetCourseSikolaByField = await session.get(
                baseUrl, params=paramsAPIGetCourseByField, ssl=False
            )

            dataCourseSikola = await responseGetCourseSikolaByField.json()
            courseIdNumber = dataCourseSikola["courses"][0]["idnumber"]
            idKelasKuliah = courseIdNumber.split(".")[1]

            await attendance_item_raw(session, baseUrl, dataCourseSikola, idKelasKuliah, itemClassError[3])


async def fetch_sikola_course():
    async with aiohttp.ClientSession() as session:
        tasks = []
        print(f"Processing Course")
        
        with open(f"data/DataExternal/{fileDataForm}", "r") as file:
            listDataDetailKelasFile = csv.reader(file, delimiter=",")
            for itemClassError in listDataDetailKelasFile:
                tasks.append(attendance_get_raw(session, itemClassError))
            await asyncio.gather(*tasks)

if __name__ == "__main__":
    kelasActiveName = "TA232.11"
    fileDataForm = "kendala_3_2.csv"
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"

    asyncio.run(fetch_sikola_course())