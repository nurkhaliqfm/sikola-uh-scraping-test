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

backupnama = "enrollcreateMAHASISWA-MAR27"

def save_backup_list(backup_list, filename=f"log/{backupnama}.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)

def load_backup_list(filename=f"log/{backupnama}.pkl"):
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

async def get_course_groups(session, baseUrl, course_id):
    paramsAPIGetCourseGroup = {
        "wsfunction": "core_group_get_course_groups",
        "courseid": course_id,
    }
    async with session.get(baseUrl, params=paramsAPIGetCourseGroup, ssl=False) as response:
        return await response.json()

async def get_enrolled_users(session, baseUrl, course_id):
    getUserPeserta = {
        "wsfunction": "core_enrol_get_enrolled_users",
        "courseid": course_id,
    }
    async with session.get(baseUrl, params=getUserPeserta, ssl=False) as response:
        return await response.json()

async def get_user_by_field(session, baseUrl, field, value):
    paramsAPIGetUserSikolaByField = {
        "wsfunction": "core_user_get_users_by_field",
        "field": field,
        "values[0]": value,
    }
    async with session.get(baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False) as response:
        return await response.json()

async def create_user(session, baseUrl, nim_upper, nim_lower, nama_mahasiswa, email, emailNim):
    paramsAPICreateUserSikolaByField = {
        "wsfunction": "core_user_create_users",
        "users[0][firstname]": nim_upper,
        "users[0][username]": nim_lower,
        "users[0][password]": nim_lower,
        "users[0][idnumber]": nim_upper,
        'users[0][lastname]': nama_mahasiswa,
        'users[0][email]': email,
    }
    async with session.get(baseUrl, params=paramsAPICreateUserSikolaByField, ssl=False) as response:
        response = response.json()
        if 'exception' in response and response['exception'] == 'invalid_parameter_exception':
            paramsAPICreateUserSikolaByField = {
                "wsfunction": "core_user_create_users",
                "users[0][firstname]": nim_upper,
                "users[0][username]": nim_lower,
                "users[0][password]": nim_lower,
                "users[0][idnumber]": nim_upper,
                'users[0][lastname]': nama_mahasiswa,
                'users[0][email]': emailNim,
            }
            print(F"BUAT USER WITH EMAIL NIM {nim_upper}")
            async with session.get(baseUrl, params=paramsAPICreateUserSikolaByField, ssl=False) as response:
                return await response.json()


        else:
            return await response

async def enroll_user(session, baseUrl, user_id, course_id):
    paramsAPIEnrollUserSikolaByField = {
        "wsfunction": "enrol_manual_enrol_users",
        "enrolments[0][roleid]": 5,
        "enrolments[0][userid]": user_id,
        'enrolments[0][courseid]': course_id,
    }
    async with session.get(baseUrl, params=paramsAPIEnrollUserSikolaByField, ssl=False) as response:
        return await response.json()

async def unenroll_user(session, baseUrl, user_id, course_id):
    paramsAPIUnenrollUserSikolaByField = {
        "wsfunction": "enrol_manual_unenrol_users",
        "enrolments[0][userid]": user_id,
        'enrolments[0][courseid]': course_id,
    }
    async with session.get(baseUrl, params=paramsAPIUnenrollUserSikolaByField, ssl=False) as response:
        return await response.json()

async def add_user_to_group(session, baseUrl, group_id, user_id):
    paramsAPIEnrollMahasiswaToGroup = {
        "wsfunction": "core_group_add_group_members",
        "members[0][groupid]": group_id,
        "members[0][userid]": user_id,
    }
    async with session.get(baseUrl, params=paramsAPIEnrollMahasiswaToGroup, ssl=False) as response:
        return await response.json()
    
    
async def update_user_email(session, baseUrl, user_id, new_email):
    paramsUpdate = {
        "wsfunction": "core_user_update_users",
        "users[0][id]": user_id,
        "users[0][email]": new_email,
    }
    async with session.get(baseUrl, params=paramsUpdate, ssl=False) as response:
        return await response.json()
    

async def process_student(session, baseUrl, course_id, mahasiswaGroupId, nim_lower, mhs_info, enrolledNIMs, tasks, errorMhs):
    nim_upper = nim_lower.upper()
    nama_mahasiswa = mhs_info["mahasiswa"]["nama_mahasiswa"].upper()
    email = mhs_info['mahasiswa']['email']
    emailNim = f"{nim_lower}@unhas.ac.id"

    if nim_lower not in enrolledNIMs:
        dataUserSikola = await get_user_by_field(session, baseUrl, "username", nim_lower)

        if len(dataUserSikola) == 0:
            try:
                dataUserBaruSikola = await create_user(session, baseUrl, nim_upper, nim_lower, nama_mahasiswa, email, emailNim)
                userId = dataUserBaruSikola[0]['id']
                print('CREATE USER', dataUserBaruSikola[0]['username'])
                tasks.append(enroll_user(session, baseUrl, userId, course_id))
                tasks.append(add_user_to_group(session, baseUrl, mahasiswaGroupId, userId))
            except Exception as e:
                
                print(f"Error READY student {nim_upper}: {e}")
                os.makedirs(f"data/User/", exist_ok=True)
                error = {
                    'nim': nim_upper,
                    'nama': mhs_info["mahasiswa"]['nama_mahasiswa']
                }
                
                errorMhs.append(error)
              
        
        else:
            userId = dataUserSikola[0]['id']
            print('UPDATE ENROLL USER', dataUserSikola[0]['username'])
            tasks.append(enroll_user(session, baseUrl, userId, course_id))
            tasks.append(add_user_to_group(session, baseUrl, mahasiswaGroupId, userId))

async def enroll_user_and_group(session, students, baseUrl, courseData, details, errorMhs):
    tasks = []

    if 'courses' in courseData and len(courseData['courses']) > 0:
        course_id = courseData['courses'][0]['id']
        dataCourseGroup = await get_course_groups(session, baseUrl, course_id)

        if dataCourseGroup:
            mahasiswaGroup = next((group for group in dataCourseGroup if group["name"] == "MAHASISWA"), None)

            if mahasiswaGroup:
                mahasiswaGroupId = mahasiswaGroup["id"]
                dataPeserta = await get_enrolled_users(session, baseUrl, course_id)
                enrolledNIMs = set()

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

                    for peserta in dataPeserta:
                        if not peserta['username'].startswith("t"):
                            username_lower = peserta["username"].lower()
                            if any(role["roleid"] == 5 for role in peserta["roles"]):
                                if username_lower not in allStudentNIMs:
                                    tasks.append(unenroll_user(session, baseUrl, peserta["id"], course_id))
                                    print('UNENROLL USER', username_lower)
                            if 'groups' in peserta and any(group["name"] == "MAHASISWA" for group in peserta["groups"]):
                                enrolledNIMs.add(peserta["username"])

                    for nim_lower, mhs_info in allStudentNIMs.items():
                        await process_student(session, baseUrl, course_id, mahasiswaGroupId, nim_lower, mhs_info, enrolledNIMs, tasks, errorMhs)

                    print(f"FISIP {details['shortname_sikola']}")

                else:
                    print(f"NON {details['shortname_sikola']}")
                    studentNIMs = set(student["mahasiswa"]["nim"].lower() for student in students)

                    for peserta in dataPeserta:
                        if not peserta['username'].startswith("t"):
                            username_lower = peserta["username"].lower()
                            if any(role["roleid"] == 5 for role in peserta["roles"]):
                                if username_lower not in studentNIMs:
                                    tasks.append(unenroll_user(session, baseUrl, peserta["id"], course_id))
                                    print('UNENROLL USER', username_lower)
                            if 'groups' in peserta and any(group["name"] == "MAHASISWA" for group in peserta["groups"]):
                                enrolledNIMs.add(peserta["username"])

                    for student in students:
                        nim_lower = student["mahasiswa"]["nim"].lower()
                        await process_student(session, baseUrl, course_id, mahasiswaGroupId, nim_lower, student, enrolledNIMs, tasks, errorMhs)

    return tasks

async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        kelasActiveName = "TA242.8"
        listDataDetailKelasFile = glob.glob(f"data/detailkelas/{kelasActiveName}/*.json")
        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=3bdff39b5f62204b247c93e852caad8b&moodlewsrestformat=json"

        loopingSize = len(listDataDetailKelasFile)
        currentFile = 0

        task = []
        errorMhs = []

        for filePath in listDataDetailKelasFile:
            currentFile += 1
            with open(filePath, "r", encoding="utf-8") as f:
                data = f.read()

            dataDetailCourse = json.loads(data)

            idnumber_sikola = dataDetailCourse["idnumber_sikola"]
            shortname_sikola = dataDetailCourse["shortname_sikola"]
            mahasiswas = dataDetailCourse["pesertaKelases"]

            print(f"Progress: {((currentFile / loopingSize) * 100):.2f} %")

            if idnumber_sikola not in backup_list:
                print(f"Shortname Course : {shortname_sikola}")

                paramsAPIGetCourseByField = {
                    "wsfunction": "core_course_get_courses_by_field",
                    "field": "idnumber",
                    "value": idnumber_sikola,
                }

                async with session.get(baseUrl, params=paramsAPIGetCourseByField, ssl=False) as responseGetCourseSikolaByField:
                    dataCourseSikola = await responseGetCourseSikolaByField.json()

                task = await enroll_user_and_group(session, mahasiswas, baseUrl, dataCourseSikola, dataDetailCourse, errorMhs)

                print(idnumber_sikola, 'ID NUMBER')

                responsesTask = await asyncio.gather(*task)
                # print(responsesTask)
                
             

                backup_list.append(idnumber_sikola)
                save_backup_list(backup_list)

        with open(f"data/User/{backupnama}.json", "w") as f:
            json.dump(errorMhs, f, indent=4)

if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())