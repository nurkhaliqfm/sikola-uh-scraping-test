import aiohttp
import asyncio
import glob
import os
import pandas as pd
import requests
import json
import pickle
import csv
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

load_dotenv()

# Disable InsecureRequestWarning
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)





async def attendance_item_raw(session, baseUrl, courseData, idKelasKuliah, classDateConverted):
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
                              
                                if (
                                    convertDate == classDateConverted
                                    and item["groupid"] == mahasiswaGroupId
                                ):
                                    resultAttendanceRaw.append(item)

                            if len(resultAttendanceRaw) > 0:
                                os.makedirs(f"data/attendanceRaw/{classDateConverted}/mahasiswa/", exist_ok=True)

                                with open(
                                    f"data/attendanceRaw/{classDateConverted}/mahasiswa/{idKelasKuliah}.json",
                                    "w",
                                ) as f:
                                    json.dump(resultAttendanceRaw, f, indent=4)
                                os.makedirs(f"data/revisiAttendanceRaw/{currentDate}/mahasiswa/", exist_ok=True)
                                with open(
                                    f"data/revisiAttendanceRaw/{currentDate}/mahasiswa/{idKelasKuliah}-{classDateConverted}.json",
                                    "w",
                                ) as f:
                                    json.dump(resultAttendanceRaw, f, indent=4)

                            break                            
                    break
    print(f"{courseData['courses'][0]['fullname']} DONE..!!")

async def attendance_get_raw(session, itemClassError):
    print(itemClassError[1])
    start_date = "2024-02-19"
    end_date = "2024-05-06"
    tasks = []
    
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")


    for date_obj in range((end_date_obj - start_date_obj).days + 1):
        current_date = (start_date_obj + timedelta(days=date_obj)).strftime("%Y-%m-%d")

        shortname_sikola = f"TA232-{itemClassError[1]}"
        paramsAPIGetCourseByField = {
            "wsfunction": "core_course_get_courses_by_field",
            "field": "shortname",
            "value": shortname_sikola,
        }

        responseGetCourseSikolaByField = await session.get(
            baseUrl, params=paramsAPIGetCourseByField, ssl=False
        )

        dataCourseSikola = await responseGetCourseSikolaByField.json()
       
        tasks.append(attendance_item_raw(session, baseUrl, dataCourseSikola, itemClassError[1], current_date))
    await asyncio.gather(*tasks)

async def fetch_sikola_course():
    async with aiohttp.ClientSession() as session:
        tasks = []
        print(f"Processing Course")
        
        if fileDataForm.endswith(".xlsx"):
            df = pd.read_excel(f"data/DataExternal/{fileDataForm}")
            unique_ids = df.drop_duplicates(subset=['id_kelas_kuliah'])[['fullname_kelas_sikola', 'id_kelas_kuliah']]

            for index, row in unique_ids.iterrows():
                tasks.append(attendance_get_raw(session, row.tolist()))
        elif fileDataForm.endswith(".csv"):
            with open(f"data/DataExternal/{fileDataForm}", "r") as file:
                listDataDetailKelasFile = csv.reader(file, delimiter=",")
                for itemClassError in listDataDetailKelasFile:
                    tasks.append(attendance_get_raw(session, itemClassError))
        else:
            print("Unsupported file format")

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    currentDate = "2024-05-03-kendala-1"

    kelasActiveName = "TA232.12"
    fileDataForm = "kendala.xlsx"
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"

    asyncio.run(fetch_sikola_course())