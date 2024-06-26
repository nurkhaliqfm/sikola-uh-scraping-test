import aiohttp
import asyncio
import glob
import os
import requests
import json
import pickle
import csv

from dotenv import load_dotenv

load_dotenv()

# Disable InsecureRequestWarning
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def save_backup_list(
    backup_list, filename="log/backup_list_enrol_mahasiswa-enrole-inbound.pkl"
):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/backup_list_enrol_mahasiswa-enrole-inbound.pkl"):
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


async def unenroll_user(session, student, baseUrl, courseData):
    task = []

    print(f"Student: {student}")
    paramsAPIGetUserSikolaByField = {
        "wsfunction": "core_user_get_users_by_field",
        "field": "username",
        "values[0]": student.lower(),
    }

    responseGetUserSikolaByField = await session.get(
        baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
    )

    dataUserSikola = await responseGetUserSikolaByField.json()
    print(dataUserSikola)

    paramsAPIEnrollUserSikolaByField = {
        "wsfunction": "enrol_manual_enrol_users",
        "enrolments[0][roleid]": 5,
        "enrolments[0][userid]": dataUserSikola[0]["id"],
        "enrolments[0][courseid]": courseData["courses"][0]["id"],
    }

    task.append(
        session.get(baseUrl, params=paramsAPIEnrollUserSikolaByField, ssl=False)
    )
    print("Student Done...")

    return task


async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
        # baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=5efd77a7277c9ef1dc42a29cb812b552&moodlewsrestformat=json"

        with open("data/DataExternal/data-kelas-inbound.csv", "r") as file:
            dataChangeFile = csv.reader(file, delimiter=",")

            # logCourseChange = json.loads(dataChangeFile)

            # loopingSize = len(dataChangeFile)
            # currentFile = 0

            for itemCourse in dataChangeFile:
                # currentFile += 1
                if not itemCourse[0] == "nim":
                    print(itemCourse)
                    shortname = f"TA232-{itemCourse[2]}"

                    # print(f"Progress: {((currentFile / loopingSize) * 100):.2f} %")

                    if itemCourse[2] not in backup_list:
                        print(f"Shortname Course : {shortname}")

                        paramsAPIGetCourseByField = {
                            "wsfunction": "core_course_get_courses_by_field",
                            "field": "shortname",
                            "value": shortname,
                        }

                        responseGetCourseSikolaByField = await session.get(
                            baseUrl, params=paramsAPIGetCourseByField, ssl=False
                        )

                        dataCourseSikola = await responseGetCourseSikolaByField.json()

                        task = await unenroll_user(
                            session,
                            itemCourse[0],
                            baseUrl,
                            dataCourseSikola,
                        )
                        respnsesTask = await asyncio.gather(*task)

                        for res in respnsesTask:
                            resultFetch.append(await res.json())

                # backup_list.append(idnumber_sikola)
                # save_backup_list(backup_list)
                # break


# get fetch_sikola_course()
if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
