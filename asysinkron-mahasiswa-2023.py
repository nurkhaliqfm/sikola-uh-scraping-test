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


def save_backup_list(backup_list, filename="log/backup_list_enrol_user2023.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/backup_list_enrol_user2023.pkl"):
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


async def enroll_user(session, students, baseUrl, courseData):
    task = []
    print("Student Enrollment...")
    for student in students:
        if not student[0] == "id":
            namaMahasiswa = student[2].upper()
            nimMahasiswa = student[3].lower()
            print(namaMahasiswa)
            # if nimMahasiswa not in backup_list:
            paramsAPIGetUserSikolaByField = {
                "wsfunction": "core_user_get_users_by_field",
                "field": "username",
                "values[0]": nimMahasiswa,
            }

            responseGetUserSikolaByField = await session.get(
                baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
            )

            dataUserSikola = await responseGetUserSikolaByField.json()

            if len(dataUserSikola) == 0:
                paramsAPICreateUserSikolaByField = {
                    "wsfunction": "core_user_create_users",
                    "users[0][firstname]": namaMahasiswa,
                    "users[0][username]": nimMahasiswa,
                    "users[0][idnumber]": nimMahasiswa,
                    "users[0][password]": f"{nimMahasiswa}@2023!",
                    "users[0][lastname]": ".",
                    "users[0][email]": f"{nimMahasiswa}@unhas.ac.id",
                }

                responseGetCreateUserSikolaByField = await session.get(
                    baseUrl, params=paramsAPICreateUserSikolaByField, ssl=False
                )

                dataUserBaruSikola = await responseGetCreateUserSikolaByField.json()
                print(paramsAPICreateUserSikolaByField)

                paramsAPIEnrollUserSikolaByField = {
                    "wsfunction": "enrol_manual_enrol_users",
                    "enrolments[0][roleid]": 5,
                    "enrolments[0][userid]": dataUserBaruSikola[0]["id"],
                    "enrolments[0][courseid]": courseData["courses"][0]["id"],
                }
            else:
                paramsAPIEnrollUserSikolaByField = {
                    "wsfunction": "enrol_manual_enrol_users",
                    "enrolments[0][roleid]": 5,
                    "enrolments[0][userid]": dataUserSikola[0]["id"],
                    "enrolments[0][courseid]": courseData["courses"][0]["id"],
                }

            task.append(
                session.get(baseUrl, params=paramsAPIEnrollUserSikolaByField, ssl=False)
            )

            # backup_list.append(nimMahasiswa)
            # save_backup_list(backup_list)

    return task


async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        # baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=2733cd661f599f6dcb60629ea3248f8c&moodlewsrestformat=json"

        with open("data/Data Mahasiswa Unhas Angkatan 2023.csv", "r") as file:
            dataMahasiswa2023 = csv.reader(file, delimiter=",")

            paramsAPIGetCourseByField = {
                "wsfunction": "core_course_get_courses_by_field",
                "field": "idnumber",
                "value": "PPKS-2024-SPADA",
            }

            responseGetCourseSikolaByField = await session.get(
                baseUrl, params=paramsAPIGetCourseByField, ssl=False
            )

            dataCourseSikola = await responseGetCourseSikolaByField.json()
            task = await enroll_user(
                session, dataMahasiswa2023, baseUrl, dataCourseSikola
            )
            respnsesTask = await asyncio.gather(*task)

            for res in respnsesTask:
                resultFetch.append(await res.json())

            print("Enrollment Done...")


# get fetch_sikola_course()
if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
