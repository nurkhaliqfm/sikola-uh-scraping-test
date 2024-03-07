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


def save_backup_list(
    backup_list, filename="log/backup_list_enrol_dosen-enrole.pkl"
):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/backup_list_enrol_dosen-enrole.pkl"):
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


async def enroll_user(session, lecturers, baseUrl, courseData):
    task = []

    print('Lecturer...') 
    for lecturer in lecturers:
        print(f"Lecturer: {lecturer['nama']}")
        paramsAPIGetUserSikolaByField = {
            "wsfunction": "core_user_get_users_by_field",
            "field": "username",
            "values[0]": lecturer["nip"].lower().replace("'",''),
        }

        responseGetUserSikolaByField = await session.get(
            baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
        )

        dataUserSikolaDosen = await responseGetUserSikolaByField.json()
        

        if len(dataUserSikolaDosen) == 0:
            paramsAPICreateDosenSikolaByField = {
                "wsfunction": "core_user_create_users",
                "users[0][firstname]":lecturer["nama"],
                "users[0][username]": lecturer["nip"].lower().replace("'",''),
                "users[0][idnumber]": lecturer["nip"].lower().replace("'",''),
                "users[0][password]": f"{lecturer["nip"].lower()}@2023!",
                'users[0][lastname]':'.',
                'users[0][email]':f"{lecturer["nip"].lower().replace("'",'')}@unhas.ac.id"
            }

            responseGetCreateDosenSikolaByField = await session.get(
                baseUrl, params=paramsAPICreateDosenSikolaByField, ssl=False
            )

            dataDosenBaruSikola = await responseGetCreateDosenSikolaByField.json()
            print(paramsAPICreateDosenSikolaByField)


            paramsAPIEnrollDosenSikolaByField = {
                "wsfunction": "enrol_manual_enrol_users",
                "enrolments[0][roleid]": 3,
                "enrolments[0][userid]": dataDosenBaruSikola[0]['id'],
                'enrolments[0][courseid]':courseData['courses'][0]['id'],
            }
        else:
            paramsAPIEnrollDosenSikolaByField = {
                "wsfunction": "enrol_manual_enrol_users",
                "enrolments[0][roleid]": 3,
                "enrolments[0][userid]": dataUserSikolaDosen[0]['id'],
                'enrolments[0][courseid]':courseData['courses'][0]['id'],
            }

        task.append(
            session.get(baseUrl, params=paramsAPIEnrollDosenSikolaByField, ssl=False)
        )
    print('Lecturer Done...') 

    return task


async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
       
        with open("data/detailkelas/ChangeItem/dosen/TA232-120037.json", "r") as f:
            dataChangeFile = f.read()

        logCourseChange = json.loads(dataChangeFile)

        loopingSize = len(logCourseChange)
        currentFile = 0

        for itemCourse in logCourseChange:
            currentFile += 1
            inM = itemCourse[3]
            if len(inM) != 0:
                idnumber_sikola = itemCourse[0]
                lecturers = inM

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

                    task = await enroll_user(
                        session,
                        lecturers,
                        baseUrl,
                        dataCourseSikola,
                    )
                    respnsesTask = await asyncio.gather(*task)

                    for res in respnsesTask:
                        print(await res.json())
                        resultFetch.append(await res.json())

                backup_list.append(idnumber_sikola)
                save_backup_list(backup_list)
                # break


# get fetch_sikola_course()
if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
