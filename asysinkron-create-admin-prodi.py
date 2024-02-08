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


def save_backup_list(backup_list, filename="log/backup_list_create_admin_prodi.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/backup_list_create_admin_prodi.pkl"):
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
# Pass email sikola
# xurkbyknptnathvw
# Adminrole id -> 1


async def create_admin_prodi(session, students, baseUrl, courseData, lecturers):
    task = []
    paramsAPIGetCourseGroup = {
        "wsfunction": "core_group_get_course_groups",
        "courseid": courseData["courses"][0]["id"],
    }

    responseGETCourseGroup = await session.get(
        baseUrl, params=paramsAPIGetCourseGroup, ssl=False
    )

    dataCourseGroup = await responseGETCourseGroup.json()
    if not len(dataCourseGroup) == 0:
        dosenGroupId = dataCourseGroup[0]["id"]
        mahasiswaGroupId = dataCourseGroup[1]["id"]

        print("Student...")
        for student in students:
            paramsAPIGetUserSikolaByField = {
                "wsfunction": "core_user_get_users_by_field",
                "field": "username",
                "values[0]": student["nim"].lower(),
            }

            responseGetUserSikolaByField = await session.get(
                baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
            )

            dataUserSikola = await responseGetUserSikolaByField.json()

            if not len(dataUserSikola) == 0:
                paramsAPIEnrollMahasiswaToGroup = {
                    "wsfunction": "core_group_add_group_members",
                    "members[0][groupid]": mahasiswaGroupId,
                    "members[0][userid]": dataUserSikola[0]["id"],
                }

                task.append(
                    session.get(
                        baseUrl, params=paramsAPIEnrollMahasiswaToGroup, ssl=False
                    )
                )

        print("Student Done...")

        # print("Lecturer...")
        # for lecturer in lecturers:
        #     paramsAPIGetUserSikolaByField = {
        #         "wsfunction": "core_user_get_users_by_field",
        #         "field": "username",
        #         "values[0]": lecturer["nip"].lower().replace("'", ""),
        #     }

        #     responseGetUserSikolaByField = await session.get(
        #         baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
        #     )

        #     dataUserSikolaDosen = await responseGetUserSikolaByField.json()

        #     if not len(dataUserSikolaDosen) == 0:
        #         paramsAPIEnrollDosenToGroup = {
        #             "wsfunction": "core_group_add_group_members",
        #             "members[0][groupid]": dosenGroupId,
        #             "members[0][userid]": dataUserSikolaDosen[0]["id"],
        #         }

        #         task.append(
        #             session.get(baseUrl, params=paramsAPIEnrollDosenToGroup, ssl=False)
        #         )
        # print("Lecturer Done...")

    return task


async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        # baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=2733cd661f599f6dcb60629ea3248f8c&moodlewsrestformat=json"

        with open("data/prodi_semester.json", "r") as f:
            data = f.read()

        dataJsonProdi = json.loads(data)
        dataProdi = dataJsonProdi["prodiSemesters"]

        loopingSize = len(dataProdi)
        current = 0

        for prodi in dataProdi:
            categoryNameSikola = prodi["prodi"]["nama_resmi"]
            categoryId = prodi["prodi"]["kode_dikti"]
            print(prodi)
        # for filePath in listDataDetailKelasFile:
        #     currentFile += 1
        #     with open(filePath, "r") as f:
        #         data = f.read()

        #     dataDetailCourse = json.loads(data)

        #     idnumber_sikola = dataDetailCourse["idnumber_sikola"]
        #     shortname_sikola = dataDetailCourse["shortname_sikola"]
        #     mahasiswas = dataDetailCourse["mahasiswas"]
        #     dosens = dataDetailCourse["dosens"]

        # print(f"Progress: {((currentFile / loopingSize) * 100):.2f} %")

        # if idnumber_sikola not in backup_list:
        #     print(f"Shortname Course : {shortname_sikola}")

        #     # if shortname_sikola == 'TA232-124999':
        #     paramsAPIGetCourseByField = {
        #         "wsfunction": "core_course_get_courses_by_field",
        #         "field": "idnumber",
        #         "value": idnumber_sikola,
        #     }

        #     responseGetCourseSikolaByField = await session.get(
        #         baseUrl, params=paramsAPIGetCourseByField, ssl=False
        #     )

        #     dataCourseSikola = await responseGetCourseSikolaByField.json()
        #     task = await create_admin_prodi(
        #         session, mahasiswas, baseUrl, dataCourseSikola, dosens
        #     )
        #     respnsesTask = await asyncio.gather(*task)

        #     for res in respnsesTask:
        #         resultFetch.append(await res.json())

        #     backup_list.append(idnumber_sikola)
        #     save_backup_list(backup_list)


# get fetch_sikola_course()
if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
