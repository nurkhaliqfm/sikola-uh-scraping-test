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
    backup_list, filename="log/backup_list_enrol_dosen-enrole-group-DOSEN.pkl"
):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/backup_list_enrol_dosen-enrole-group-DOSEN.pkl"):
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
    tasks = []
    paramsAPIGetCourseGroup = {
        "wsfunction": "core_group_get_course_groups",
        "courseid": courseData["courses"][0]["id"],
    }

    responseGETCourseGroup = await session.get(
        baseUrl, params=paramsAPIGetCourseGroup, ssl=False
    )

    dataCourseGroup = await responseGETCourseGroup.json()

    if dataCourseGroup:
        
        namaGroup = dataCourseGroup[0]["name"]
        
        if namaGroup == "DOSEN" :
            dosenGroupId = dataCourseGroup[0]["id"]
            for lecturer in lecturers:
                print(namaGroup, namaGroup, lecturer['nama'])
                paramsAPIGetUserSikolaByField = {
                    "wsfunction": "core_user_get_users_by_field",
                    "field": "idnumber",
                    "values[0]": lecturer["id"]
                }

                responseGetUserSikolaByField = await session.get(
                    baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
                )

                dataUserSikolaDosen = await responseGetUserSikolaByField.json()
                
                if not len(dataUserSikolaDosen) == 0:
                  
                    paramsAPIEnrollDosenToGroup = {
                        "wsfunction": "core_group_add_group_members",
                        "members[0][groupid]": dosenGroupId,
                        "members[0][userid]": dataUserSikolaDosen[0]["id"],
                    }

                    tasks.append(
                        session.get(baseUrl, params=paramsAPIEnrollDosenToGroup, ssl=False)
                    )
               
            print("Lecturer Done...")

    return tasks


async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        
        kelasActiveName = "TA241.1"
        # kelasActiveName = "TEST"
        listDataDetailKelasFile = glob.glob(
            f"data/detailkelas/{kelasActiveName}/*.json"
        )
        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"

        # with open("data/detailkelas/ChangeItem/dosen/TA232-119266.json", "r") as f:
        #     dataChangeFile = f.read()

        # logCourseChange = json.loads(dataChangeFile)

        loopingSize = len(listDataDetailKelasFile)
        currentFile = 0

        for filePath in listDataDetailKelasFile:
            currentFile += 1
            inM = filePath[3]
            
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
                    dosens,
                    baseUrl,
                    dataCourseSikola,
                )
                respnsesTask = await asyncio.gather(*task)

                for res in respnsesTask:
                    resultFetch.append(await res.json())

            backup_list.append(idnumber_sikola)
            save_backup_list(backup_list)
                # break


# get fetch_sikola_course()
if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
