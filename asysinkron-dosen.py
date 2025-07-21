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


def save_backup_list(backup_list, filename="log/updateIDNumber-29aug.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/updateIDNumber-29aug.pkl"):
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





async def update_user(session, students, baseUrl, courseData, sizeUser, lecturers):
    task = []
    print('Lecturer...') 
    for lecturer in lecturers:
        paramsAPIGetUserSikolaByField = {
            "wsfunction": "core_user_get_users_by_field",
            "field": "username",
            "values[0]": lecturer["nip"].lower().replace("'",''),
        }

        responseGetUserSikolaByField = await session.get(
            baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
        )

        dataUserSikolaDosen = await responseGetUserSikolaByField.json()
        
        if (dataUserSikolaDosen):
            
            print(lecturer['id'])
            
            if "idnumber" not in dataUserSikolaDosen[0] or not dataUserSikolaDosen[0]["idnumber"] or dataUserSikolaDosen[0]["idnumber"] != int(lecturer['id']):
                
                paramsUpdate = {
                    "wsfunction": "core_user_update_users",
                    "users[0][id]": dataUserSikolaDosen[0]["id"],
                    "users[0][idnumber]": lecturer["id"]
                }
                
                print('change DOSEN ', lecturer['nip'])
                
                responseGetCreateUserSikolaByField = await session.get(
                    baseUrl, params=paramsUpdate, ssl=False
                )
                
                
                print(await responseGetCreateUserSikolaByField.json())

               
            
            
        

       
    print('Lecturer Done...') 

    return task



async def enroll_user(session, students, baseUrl, courseData, sizeUser, lecturers):
    task = []
    print('Lecturer...') 
    for lecturer in lecturers:
        paramsAPIGetUserSikolaByField = {
            "wsfunction": "core_user_get_users_by_field",
            "field": "idnumber",
            "values[0]": lecturer["id"],
        }
        
        try:
            responseGetUserSikolaByField = await session.get(
                baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
            )

            dataUserSikolaDosen = await responseGetUserSikolaByField.json()

            if len(dataUserSikolaDosen) == 0:
                paramsAPICreateDosenSikolaByField = {
                    "wsfunction": "core_user_create_users",
                    "users[0][username]": lecturer['nip'].lower().replace("'",''),
                    "users[0][password]": lecturer['nip'].lower().replace("'",''),
                    "users[0][idnumber]": lecturer['id'],
                    'users[0][firstname]': '.',
                    "users[0][lastname]": lecturer['nama'],
                    'users[0][email]': f"{lecturer['nip'].lower()}@unhas.ac.id"
                }

                responseGetCreateDosenSikolaByField = await session.get(
                    baseUrl, params=paramsAPICreateDosenSikolaByField, ssl=False
                )

                dataDosenBaruSikola = await responseGetCreateDosenSikolaByField.json()
                print(paramsAPICreateDosenSikolaByField)

                # Check if courseData['courses'] exists and has at least one element
                if 'courses' in courseData and len(courseData['courses']) > 0:
                    course_id = courseData['courses'][0]['id']
                else:
                    print(f"No courses found for lecturer {lecturer['nama']}, skipping...")
                    continue

                paramsAPIEnrollDosenSikolaByField = {
                    "wsfunction": "enrol_manual_enrol_users",
                    "enrolments[0][roleid]": 3,
                    "enrolments[0][userid]": dataDosenBaruSikola[0]['id'],
                    'enrolments[0][courseid]': course_id,
                }
            else:
                # Check if courseData['courses'] exists and has at least one element
                if 'courses' in courseData and len(courseData['courses']) > 0:
                    course_id = courseData['courses'][0]['id']
                else:
                    print(f"No courses found for lecturer {lecturer['nama']}, skipping...")
                    continue

                paramsAPIEnrollDosenSikolaByField = {
                    "wsfunction": "enrol_manual_enrol_users",
                    "enrolments[0][roleid]": 3,
                    "enrolments[0][userid]": dataUserSikolaDosen[0]['id'],
                    'enrolments[0][courseid]': course_id,
                }

            task.append(
                session.get(baseUrl, params=paramsAPIEnrollDosenSikolaByField, ssl=False)
            )

        except Exception as e:
            print(f"Error making request for lecturer {lecturer['nama']}: {e}")

        print('Lecturer Done...')

    return task

async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        kelasActiveName = "TA241.12"
        # kelasActiveName = "TEST"
        listDataDetailKelasFile = glob.glob(
            f"data/detailkelas/{kelasActiveName}/*.json"
        )
        # baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"

        loopingSize = len(listDataDetailKelasFile)
        currentFile = 0

        for filePath in listDataDetailKelasFile:
            currentFile += 1
            with open(filePath, "r", encoding="utf-8") as f:
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
                # if shortname_sikola == 'TA232-124999':
                paramsAPIGetCourseByField = {
                    "wsfunction": "core_course_get_courses_by_field",
                    "field": "idnumber",
                    "value": idnumber_sikola,
                }

                responseGetCourseSikolaByField = await session.get(
                    baseUrl, params=paramsAPIGetCourseByField, ssl=False
                )

                dataCourseSikola = await responseGetCourseSikolaByField.json()
                
                # task = await enroll_user(
                #     session, mahasiswas, baseUrl, dataCourseSikola, sizeUserInCourse, dosens
                # )
                task = await update_user(
                    session, mahasiswas, baseUrl, dataCourseSikola, sizeUserInCourse, dosens
                )
                respnsesTask = await asyncio.gather(*task)

                for res in respnsesTask:
                    resultFetch.append(await res.json())

                backup_list.append(idnumber_sikola)
                save_backup_list(backup_list)


# get fetch_sikola_course()
if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
