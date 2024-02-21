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


def save_backup_list(backup_list, filename="log/list_new_course-from-v3.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/list_new_course-from-v3.pkl"):
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


async def enroll_user(session, students, baseUrl, courseData, sizeUser, lecturers):
    task = []
    print('Student...') 
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

        if len(dataUserSikola) == 0:
            paramsAPICreateUserSikolaByField = {
                "wsfunction": "core_user_create_users",
                "users[0][firstname]":student["nama_mahasiswa"],
                "users[0][username]": student["nim"].lower(),
                "users[0][idnumber]": student["nim"].upper(),
                "users[0][password]": f"{student["nim"].lower()}@2023!",
                'users[0][lastname]':'.',
                'users[0][email]':f"{student["nim"].lower()}@unhas.ac.id"
            }

            responseGetCreateUserSikolaByField = await session.get(
                baseUrl, params=paramsAPICreateUserSikolaByField, ssl=False
            )

            dataUserBaruSikola = await responseGetCreateUserSikolaByField.json()
            print(paramsAPICreateUserSikolaByField)

            paramsAPIEnrollUserSikolaByField = {
                "wsfunction": "enrol_manual_enrol_users",
                "enrolments[0][roleid]": 5,
                "enrolments[0][userid]": dataUserBaruSikola[0]['id'],
                'enrolments[0][courseid]':courseData['courses'][0]['id'],
            }
        else:
            paramsAPIEnrollUserSikolaByField = {
                "wsfunction": "enrol_manual_enrol_users",
                "enrolments[0][roleid]": 5,
                "enrolments[0][userid]": dataUserSikola[0]['id'],
                'enrolments[0][courseid]':courseData['courses'][0]['id'],
            }

        task.append(
            session.get(baseUrl, params=paramsAPIEnrollUserSikolaByField, ssl=False)
        )
    print('Student Done...') 
        
    return task


async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        # kelasActiveNameNewVer = "TA232.1"
        # kelasActiveNameNewVer = "TA232.2"
        # kelasActiveNameNewVer = "TA232.3"
        kelasActiveNameNewVer = "TA232.4"
        listDataDetailKelasFileNewVer = glob.glob(
            f"data/detailkelas/{kelasActiveNameNewVer}/*.json"
        )
        
        # kelasActiveNameOldVer = "TA232.1"
        # kelasActiveNameOldVer = "TA232.2"
        kelasActiveNameOldVer = "TA232.3"
        listDataDetailKelasFileOldVer = glob.glob(
            f"data/detailkelas/{kelasActiveNameOldVer}/*.json"
        )
        
        # baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=2733cd661f599f6dcb60629ea3248f8c&moodlewsrestformat=json"

        loopingSize = len(listDataDetailKelasFileNewVer)
        currentFile = 0
        listCourseStudentChange = []
        
        for filePath in listDataDetailKelasFileOldVer:
            currentFile += 1
            splitOldPathFileName = filePath.split("/")[3]
            newFilePath = f"data/detailkelas/{kelasActiveNameNewVer}/{splitOldPathFileName}"
            cekAksesFileNew  = os.path.isfile(newFilePath)
        
            if cekAksesFileNew:
                itemDataChange = []
                # print(f"file found: {newFilePath}")
                
                with open(filePath, "r") as f:
                    dataOld = f.read()
                    
                
                    
                dataDetailCourseOld = json.loads(dataOld) 
                mahasiswasOld = dataDetailCourseOld["mahasiswas"]
                
                with open(newFilePath, "r") as f:
                    dataNew = f.read()
                    
                dataDetailCourseNew = json.loads(dataNew) 
                mahasiswasNew = dataDetailCourseNew["mahasiswas"]
                
                idnumber_sikola = dataDetailCourseNew["idnumber_sikola"]
                itemDataChange.append(idnumber_sikola)
                itemDataChange.append(newFilePath)
        
                outM = []
                inM = []
                
                # FINDING OUT STUDENTS
                for mOld in mahasiswasOld:
                    found_in_mnew = False
                    for mNew in mahasiswasNew:
                        if mOld['id_user'] == mNew['id_user']:
                            found_in_mnew = True
                            break
                    if not found_in_mnew:
                        outM.append(mOld)
                        # outM.append(mOld['nama_mahasiswa'])
                
                # FINDING IN STUDENTS
                for mNew in mahasiswasNew:
                    found_in_mold = False
                    for mOld in mahasiswasOld:
                        if mOld['id_user'] == mNew['id_user']:
                            found_in_mold = True
                            break
                    if not found_in_mold:
                        inM.append(mNew)
                        # inM.append(mNew['nama_mahasiswa'])
                
                itemDataChange.append(outM)
                itemDataChange.append(inM)
                
                listCourseStudentChange.append(itemDataChange)

        with open('data/detailkelas/ChangeItem/mahasiswa/log-3.json', "w") as json_file:
            json.dump(listCourseStudentChange, json_file)


# get fetch_sikola_course()
if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
