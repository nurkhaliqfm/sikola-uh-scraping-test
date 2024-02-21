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


def save_backup_list(backup_list, filename="log/backup_list_enrol_userinbound.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/backup_list_enrol_userinbound.pkl"):
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


async def enroll_user(session, students, baseUrl):
    task = []
    print("Student Create...")
    for student in students:
        if not student[0] == "username":
            namaMahasiswa = student[1].upper()
            nimMahasiswa = student[0].lower()
            idNumberMahasiswa = student[0]
            emailMahasiswa = student[3].lower()

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
                    "users[0][idnumber]": idNumberMahasiswa,
                    "users[0][password]": f"{nimMahasiswa}@2023!",
                    "users[0][lastname]": ".",
                    "users[0][email]": emailMahasiswa,
                }

                # responseGetCreateUserSikolaByField = await session.get(
                #     baseUrl, params=paramsAPICreateUserSikolaByField, ssl=False
                # )

                task.append(
                    session.get(
                        baseUrl, params=paramsAPICreateUserSikolaByField, ssl=False
                    )
                )

                # dataUserBaruSikola = await responseGetCreateUserSikolaByField.json()
                # print(paramsAPICreateUserSikolaByField)

                # paramsAPIEnrollUserSikolaByField = {
                #     "wsfunction": "enrol_manual_enrol_users",
                #     "enrolments[0][roleid]": 5,
                #     "enrolments[0][userid]": dataUserBaruSikola[0]["id"],
                #     "enrolments[0][courseid]": courseData["courses"][0]["id"],
                # }
            # else:
            #     paramsAPIEnrollUserSikolaByField = {
            #         "wsfunction": "enrol_manual_enrol_users",
            #         "enrolments[0][roleid]": 5,
            #         "enrolments[0][userid]": dataUserSikola[0]["id"],
            #         "enrolments[0][courseid]": courseData["courses"][0]["id"],
            #     }

            # backup_list.append(nimMahasiswa)
            # save_backup_list(backup_list)

    return task


async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        # baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=b3d938f63abaf8523a094cc0fe0c8bf4&moodlewsrestformat=json"

        with open("data/DataExternal/Data NIM Tamu Mahasiswa InBound.csv", "r") as file:
            dataMahasiswaInbound = csv.reader(file, delimiter=",")

            # paramsAPIGetCourseByField = {
            #     "wsfunction": "core_course_get_courses_by_field",
            #     "field": "idnumber",
            #     "value": "PPKS-2024-SPADA",
            # }

            # responseGetCourseSikolaByField = await session.get(
            #     baseUrl, params=paramsAPIGetCourseByField, ssl=False
            # )

            # dataCourseSikola = await responseGetCourseSikolaByField.json()
            task = await enroll_user(session, dataMahasiswaInbound, baseUrl)
            respnsesTask = await asyncio.gather(*task)

            for res in respnsesTask:
                dataResp = await res.json()
                print(dataResp)
                resultFetch.append(await res.json())

            print("Create Student Done...")


# get fetch_sikola_course()
if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
