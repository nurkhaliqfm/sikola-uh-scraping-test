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


def save_backup_list(backup_list, filename="log/backup_list_enrol_dosen-unenrole.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/backup_list_enrol_dosen-unenrole.pkl"):
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


async def unenroll_user(session, lecturers, baseUrl, courseData):
    task = []

    if len(courseData["courses"]) != 0:
        print("Lecturer...")
        for lecturer in lecturers:
            print(f"Lecturer: {lecturer['nama']}")
            paramsAPIGetUserSikolaByField = {
                "wsfunction": "core_user_get_users_by_field",
                "field": "username",
                "values[0]": lecturer["nip"].lower().replace("'", ""),
            }

            responseGetUserSikolaByField = await session.get(
                baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
            )

            dataUserSikola = await responseGetUserSikolaByField.json()

            paramsAPICreateUserSikolaByField = {
                "wsfunction": "enrol_manual_unenrol_users",
                "enrolments[0][courseid]": courseData["courses"][0]["id"],
                "enrolments[0][userid]": dataUserSikola[0]["id"],
            }

            task.append(
                session.get(baseUrl, params=paramsAPICreateUserSikolaByField, ssl=False)
            )
        print("Lecturer Done...")

    return task


async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        # baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=2733cd661f599f6dcb60629ea3248f8c&moodlewsrestformat=json"

        with open("data/detailkelas/ChangeItem/dosen/log-3.json", "r") as f:
            dataChangeFile = f.read()

        logCourseChange = json.loads(dataChangeFile)

        loopingSize = len(logCourseChange)
        currentFile = 0

        for itemCourse in logCourseChange:
            currentFile += 1
            outM = itemCourse[2]
            if len(outM) != 0:
                idnumber_sikola = itemCourse[0]
                lecturers = outM

                print(f"Progress: {((currentFile / loopingSize) * 100):.2f} %")
                if idnumber_sikola not in backup_list:
                    print(f"Shortname Course : {idnumber_sikola}")
                    paramsAPIGetCourseByField = {
                        "wsfunction": "core_course_get_courses_by_field",
                        "field": "idnumber",
                        "value": idnumber_sikola,
                    }

                    responseGetCourseSikolaByField = await session.get(
                        baseUrl, params=paramsAPIGetCourseByField, ssl=False
                    )

                    dataCourseSikola = await responseGetCourseSikolaByField.json()

                    task = await unenroll_user(
                        session,
                        lecturers,
                        baseUrl,
                        dataCourseSikola,
                    )
                    respnsesTask = await asyncio.gather(*task)

                    for res in respnsesTask:
                        resultFetch.append(await res.json())

                backup_list.append(idnumber_sikola)
                save_backup_list(backup_list)


# get fetch_sikola_course()
if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
