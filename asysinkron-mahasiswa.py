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


def save_backup_list(backup_list, filename="log//updetIdtoNIM-22Jan-2.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/updetIdtoNIM-22Jan-2.pkl"):
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

async def update_user(session, students, baseUrl, courseData, details):
    task = []
    print('MHS...') 
    
    if details['is_blok'] == 0 and len(details['children']) > 0:
        allStudentNIMs = {}
        for child in details['children']:
            mahasiswasChild = child['mahasiswas']
            if len(mahasiswasChild) > 0:
                for mhs in mahasiswasChild:
                    allStudentNIMs[mhs["nim"].lower()] = {
                        "nama_mahasiswa": mhs["nama_mahasiswa"], 
                        "id": mhs["id"], 
                        "email": mhs.get("email")
                    }
        for nim_lower, mhs_info in allStudentNIMs.items():
            nim_upper = nim_lower.upper()
            paramsAPIGetUserSikolaByField = {
                "wsfunction": "core_user_get_users_by_field",
                "field": "username",
                "values[0]": nim_lower,
            }

            responseGetUserSikolaByField = await session.get(
                baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
            )

            dataUserSikolaMhs = await responseGetUserSikolaByField.json()
            if (dataUserSikolaMhs):
                 if "idnumber" not in dataUserSikolaMhs[0] or not dataUserSikolaMhs[0]["idnumber"] or dataUserSikolaMhs[0]["idnumber"] != nim_upper:
                     
                      async with session.get(baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False) as responseGetUserSikolaByField:
                        dataUserSikolaMhs = await responseGetUserSikolaByField.json()
                        if dataUserSikolaMhs:
                            if "idnumber" not in dataUserSikolaMhs[0] or not dataUserSikolaMhs[0]["idnumber"] or dataUserSikolaMhs[0]["idnumber"] != nim_upper:
                                paramsUpdate = {
                                    "wsfunction": "core_user_update_users",
                                    "users[0][id]": dataUserSikolaMhs[0]["id"],
                                    "users[0][idnumber]": nim_upper
                                }
                                
                                print('change MAHASISWA ID NUMBER ', nim_upper)
                                
                                async with session.get(baseUrl, params=paramsUpdate, ssl=False) as responseGetCreateUserSikolaByField:
                                    dataUserUpdateSikola = await responseGetCreateUserSikolaByField.json()

                    
                                    print('change MAHASISWA ID NUMBER ', student['nim'])
                    
     

                # if (int(dataUserSikolaMhs[0]['idnumber']) != int(student['id'])):
                    # print(dataUserSikolaMhs[0]["id"])
                    
                    # paramsUpdate = {
                    #     "wsfunction": "core_user_update_users",
                    #     "users[0][id]": dataUserSikolaMhs[0]["id"],
                    #     "users[0][idnumber]": nim_upper
                    # }
                    
                    # print('change MAHASISWA ID NUMBER ', nim_upper)
                    
                    # responseGetCreateUserSikolaByField = await session.get(
                    #     baseUrl, params=paramsUpdate, ssl=False
                    # )

                    # dataUserUpdateSikola = await responseGetCreateUserSikolaByField.json()

    else:
        for student in students:
            paramsAPIGetUserSikolaByField = {
                "wsfunction": "core_user_get_users_by_field",
                "field": "username",
                "values[0]": student["nim"].lower(),
            }

            responseGetUserSikolaByField = await session.get(
                baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
            )

            dataUserSikolaMhs = await responseGetUserSikolaByField.json()
            
            if (dataUserSikolaMhs):
                if "idnumber" not in dataUserSikolaMhs[0] or not dataUserSikolaMhs[0]["idnumber"] or dataUserSikolaMhs[0]["idnumber"] != student['nim'].upper():

                # if (int(dataUserSikolaMhs[0]['idnumber']) != int(student['id'])):
                    # print(dataUserSikolaMhs[0]["id"])
                    
                    # paramsUpdate = {
                    #     "wsfunction": "core_user_update_users",
                    #     "users[0][id]": dataUserSikolaMhs[0]["id"],
                    #     "users[0][idnumber]": student["nim"].upper()
                    # }
                    
                    
                    async with session.get(baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False) as responseGetUserSikolaByField:
                        dataUserSikolaMhs = await responseGetUserSikolaByField.json()
                        if dataUserSikolaMhs:
                            if "idnumber" not in dataUserSikolaMhs[0] or not dataUserSikolaMhs[0]["idnumber"] or dataUserSikolaMhs[0]["idnumber"] != nim_upper:
                                paramsUpdate = {
                                    "wsfunction": "core_user_update_users",
                                    "users[0][id]": dataUserSikolaMhs[0]["id"],
                                    "users[0][idnumber]": student["nim"].upper()
                                }
                                
                                print('change MAHASISWA ID NUMBER ', nim_upper)
                                
                                async with session.get(baseUrl, params=paramsUpdate, ssl=False) as responseGetCreateUserSikolaByField:
                                    dataUserUpdateSikola = await responseGetCreateUserSikolaByField.json()

                    
                                    print('change MAHASISWA ID NUMBER ', student['nim'])
                    
                    # responseGetCreateUserSikolaByField = await session.get(
                    #     baseUrl, params=paramsUpdate, ssl=False
                    # )

                    # dataUserUpdateSikola = await responseGetCreateUserSikolaByField.json()
                    # # print(dataUserUpdateSikola)
                
            
        

       
    print('MAHASISWA Done...') 

    return task



async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        # kelasActiveName = "TA232.2"
        kelasActiveName = "TA241.19"
        listDataDetailKelasFile = glob.glob(
            f"data/detailkelas/{kelasActiveName}/*.json"
        )
        # baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=99bb1320ef22fc37619dd027659e8d94&moodlewsrestformat=json"

        loopingSize = len(listDataDetailKelasFile)
        currentFile = 0
        
        task = []

        for filePath in listDataDetailKelasFile:
            currentFile += 1
            with open(filePath, "r", encoding="utf-8") as f:
                data = f.read()

            dataDetailCourse = json.loads(data)

            idnumber_sikola = dataDetailCourse["idnumber_sikola"]
            shortname_sikola = dataDetailCourse["shortname_sikola"]
            mahasiswas = dataDetailCourse["mahasiswas"]
            # dosens = dataDetailCourse["dosens"]
            # sizeUserInCourse = len(dataDetailCourse["mahasiswas"]) + len(
            #     dataDetailCourse["dosens"]
            # )

            print(f"Progress: {((currentFile / loopingSize) * 100):.2f} %")

            if idnumber_sikola not in backup_list:
                print(f"Shortname Course : {shortname_sikola}")

                paramsAPIGetCourseByField = {
                    "wsfunction": "core_course_get_courses_by_field",
                    "field": "idnumber",
                    "value": idnumber_sikola,
                }

                async with session.get(
                    baseUrl, params=paramsAPIGetCourseByField, ssl=False
                ) as responseGetCourseSikolaByField:
                    dataCourseSikola = await responseGetCourseSikolaByField.json()

                task = await update_user(
                    session, mahasiswas, baseUrl, dataCourseSikola, dataDetailCourse
                )
                
                print(idnumber_sikola, 'ID NUMBER')

                respnsesTask = await asyncio.gather(*task)

                for res in respnsesTask:
                    resultFetch.append(await res.json())

                backup_list.append(idnumber_sikola)
                save_backup_list(backup_list)


if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
