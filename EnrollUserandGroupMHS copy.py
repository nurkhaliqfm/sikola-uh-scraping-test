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

backupnama = "enrollcreateMAHASISWA-groups23Aug-1"
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



async def enroll_user_and_group(session, students, baseUrl, courseData, details, errorMhs):
    tasks = []
    
    
    if 'courses' in courseData and len(courseData['courses']) > 0:
 
        course_id = courseData['courses'][0]['id']
        

        # Dapatkan daftar grup di course
        paramsAPIGetCourseGroup = {
            "wsfunction": "core_group_get_course_groups",
            "courseid": course_id,
        }

        responseGETCourseGroup = await session.get(
            baseUrl, params=paramsAPIGetCourseGroup, ssl=False
        )
        dataCourseGroup = await responseGETCourseGroup.json()

        if dataCourseGroup:
            # Cari grup dengan nama MAHASISWA
            mahasiswaGroup = next(
                (group for group in dataCourseGroup if group["name"] == "MAHASISWA"), None
            )
            
            if mahasiswaGroup:
                mahasiswaGroupId = mahasiswaGroup["id"]

                # Dapatkan daftar peserta yang sudah terdaftar di course
                getUserPeserta = {
                    "wsfunction": "core_enrol_get_enrolled_users",
                    "courseid": course_id,
                }

                responseGetPeserta = await session.get(
                    baseUrl, params=getUserPeserta, ssl=False
                )
                dataPeserta = await responseGetPeserta.json()

                # Buat set untuk menyimpan nim peserta yang sudah di grup MAHASISWA
                enrolledNIMs = set()
                
                if details['is_blok'] == 0 and len(details['children']) > 0 :
                    childrens= details['children']
                    
                    for child in childrens :
                        mahasiswasChild = child['mahasiswas']
                        
                    
                        print(f"BLOK-0 children {mahasiswasChild}")
                    
                else:
                    print(details['shortname_sikola'])
                
                    # studentNIMs = set(student["nim"].lower() for student in students)

                    # for peserta in dataPeserta:
                    #     username_lower = peserta["username"].lower()
                        
                    #     if any(role["roleid"] == 5 for role in peserta["roles"]):
                    #         if username_lower not in studentNIMs:
                    #             paramsAPIUnenrollUserSikolaByField = {
                    #                 "wsfunction": "enrol_manual_unenrol_users",
                    #                 "enrolments[0][userid]": peserta["id"],
                    #                 'enrolments[0][courseid]': course_id,
                    #             }
                    #             tasks.append(
                    #                 session.get(baseUrl, params=paramsAPIUnenrollUserSikolaByField, ssl=False)
                    #             )
                    #             print('UNENROLL USER', username_lower)
                            
                    #     if 'groups' in peserta and any(group["name"] == "MAHASISWA" for group in peserta["groups"]):
                    #         enrolledNIMs.add(peserta["username"])

                    # # Loop untuk setiap student
                    

                    # for student in students:
                    #     nim_lower = student["nim"].lower()
                        
                    #     print(nim_lower)       
                    #     try:   
                    #         if nim_lower not in enrolledNIMs:
                    #             paramsAPIGetUserSikolaByFieldUpdate = {
                    #                 "wsfunction": "core_user_get_users_by_field",
                    #                 "field": "username",
                    #                 "values[0]": nim_lower,
                    #             }
                                
                    #             async with session.get(
                    #                 baseUrl, params=paramsAPIGetUserSikolaByFieldUpdate, ssl=False
                    #             ) as responseGetUserSikolaByField:
                    #                 dataUserSikola = await responseGetUserSikolaByField.json()
                        
                    #             if len(dataUserSikola) == 0:
                    #                 # Jika pengguna belum ada, buat akun
                    #                 email = student["email"] or f"{nim_lower}@unhas.ac.id"
                    #                 paramsAPICreateUserSikolaByField = {
                    #                     "wsfunction": "core_user_create_users",
                    #                     "users[0][firstname]": student["nim"].upper(),
                    #                     "users[0][username]": nim_lower,
                    #                     "users[0][password]": nim_lower,
                    #                     "users[0][idnumber]": student["id"],
                    #                     'users[0][lastname]': student["nama_mahasiswa"].upper(),
                    #                     'users[0][email]': email,
                    #                 }
                                    
                    #                 responseGetCreateDosenSikolaByFieldCreate = await session.get(
                    #                     baseUrl, params=paramsAPICreateUserSikolaByField, ssl=False
                    #                 )
                                    
                    #                 dataUserBaruSikola = await responseGetCreateDosenSikolaByFieldCreate.json()


                    #                 # async with session.get(
                    #                 #     baseUrl, params=paramsAPICreateUserSikolaByField, ssl=False
                    #                 # ) as responseGetCreateUserSikolaByField:
                    #                 #     dataUserBaruSikola = await responseGetCreateUserSikolaByField.json()

                    #                 userId = dataUserBaruSikola[0]['id']
                    #                 print('CREATE USER', dataUserBaruSikola[0]['username'])
                    #                 paramsAPIEnrollUserSikolaByFieldCreate = {
                    #                     "wsfunction": "enrol_manual_enrol_users",
                    #                     "enrolments[0][roleid]": 5,
                    #                     "enrolments[0][userid]": dataUserBaruSikola[0]['id'],
                    #                     'enrolments[0][courseid]': course_id,
                    #                 }
                    #                 tasks.append(
                    #                     session.get(baseUrl, params=paramsAPIEnrollUserSikolaByFieldCreate, ssl=False)
                    #                 )
                                    
                    #                 paramsAPIEnrollMahasiswaToGroupCreate = {
                    #                     "wsfunction": "core_group_add_group_members",
                    #                     "members[0][groupid]": mahasiswaGroupId,
                    #                     "members[0][userid]": dataUserBaruSikola[0]['id'],
                    #                 }
                                    
                    #                 tasks.append(
                    #                     session.get(baseUrl, params=paramsAPIEnrollMahasiswaToGroupCreate, ssl=False)
                    #                 )
                                    
                    #             else:
                    #                 # Jika pengguna sudah ada
                    #                 userId = dataUserSikola[0]['id']
                    #                 print('UPDATE ENROll USER', dataUserSikola[0]['username'])

                    #             # Enroll user ke course
                    #             paramsAPIEnrollUserSikolaByField = {
                    #                 "wsfunction": "enrol_manual_enrol_users",
                    #                 "enrolments[0][roleid]": 5,
                    #                 "enrolments[0][userid]": userId,
                    #                 'enrolments[0][courseid]': course_id,
                    #             }
                    #             tasks.append(
                    #                 session.get(baseUrl, params=paramsAPIEnrollUserSikolaByField, ssl=False)
                    #             )
                                
                                
                    #             paramsUpdate = {
                    #                 "wsfunction": "core_user_update_users",
                    #                 "users[0][id]": userId,
                    #                 "users[0][idnumber]": student["id"]
                    #             }
                    #             tasks.append(
                    #                 session.get(baseUrl, params=paramsUpdate, ssl=False)
                    #             )

                    #             # Enroll user ke grup MAHASISWA
                    #             paramsAPIEnrollMahasiswaToGroup = {
                    #                 "wsfunction": "core_group_add_group_members",
                    #                 "members[0][groupid]": mahasiswaGroupId,
                    #                 "members[0][userid]": userId,
                    #             }
                    #             tasks.append(
                    #                 session.get(baseUrl, params=paramsAPIEnrollMahasiswaToGroup, ssl=False)
                    #             )
                            
                            
                    #     except Exception as e:
                    #         print(f"Error processing READY student {student['nim']}: {e}")
                    #         os.makedirs(f"data/User/", exist_ok=True)
                    #         error = {
                    #             'nim': student['nim'],
                    #             'nama': student['nama_mahasiswa']
                    #         }
                            
                    #         errorMhs.append(error)
                    
                    
                
                        
                        
    
    # else:
    #     for student in students:
    #         nim_lower = student["nim"].lower()       
    #         try:   
    #             paramsAPIGetUserSikolaByFieldUpdate = {
    #                 "wsfunction": "core_user_get_users_by_field",
    #                 "field": "username",
    #                 "values[0]": nim_lower,
    #             }
                
    #             async with session.get(
    #                 baseUrl, params=paramsAPIGetUserSikolaByFieldUpdate, ssl=False
    #             ) as responseGetUserSikolaByField:
    #                 dataUserSikola = await responseGetUserSikolaByField.json()
        
    #             if len(dataUserSikola) == 0:
    #                 email = student["mahasiswa"]["email"] or f"{nim_lower}@unhas.ac.id"
    #                 paramsAPICreateUserSikolaByField = {
    #                     "wsfunction": "core_user_create_users",
    #                     "users[0][firstname]": student["mahasiswa"]["nim"].upper(),
    #                     "users[0][username]": nim_lower,
    #                     "users[0][password]": nim_lower,
    #                     "users[0][idnumber]": student["mahasiswa"]["id"],
    #                     'users[0][lastname]': student["mahasiswa"]["nama_mahasiswa"].upper(),
    #                     'users[0][email]': email,
    #                 }

    #                 async with session.get(
    #                     baseUrl, params=paramsAPICreateUserSikolaByField, ssl=False
    #                 ) as responseGetCreateUserSikolaByField:
    #                     dataUserBaruSikola = await responseGetCreateUserSikolaByField.json()

    #                 userId = dataUserBaruSikola[0]['id']
    #                 print('CREATE NONE USER', dataUserBaruSikola[0]['username'])
                    
    #             else:
    #                 userId = dataUserSikola[0]['id']
    #                 print('UPDATE NONE USER', dataUserSikola[0]['username'])

    #             paramsUpdate = {
    #                 "wsfunction": "core_user_update_users",
    #                 "users[0][id]": userId,
    #                 "users[0][idnumber]": student["mahasiswa"]["id"]
    #             }
    #             tasks.append(
    #                 session.get(baseUrl, params=paramsUpdate, ssl=False)
    #             )

    #         except Exception as e:
    #             print(f"Error processing NONE student {student['nim']}: {e}")
    
    
    
    return tasks






async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        # kelasActiveName = "TA232.2"
        kelasActiveName = "TA241.11"
        listDataDetailKelasFile = glob.glob(
            f"data/detailkelas/{kelasActiveName}/*.json"
        )
        # baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"

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
            mahasiswas = dataDetailCourse["mahasiswas"]
            dosens = dataDetailCourse["dosens"]
            sizeUserInCourse = len(dataDetailCourse["mahasiswas"]) + len(
                dataDetailCourse["dosens"]
            )

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

                task = await enroll_user_and_group(
                    session, mahasiswas, baseUrl, dataCourseSikola, dataDetailCourse, errorMhs
                )
                
                print(idnumber_sikola, 'ID NUMBER')

                respnsesTask = await asyncio.gather(*task)

                for res in respnsesTask:
                    resultFetch.append(await res.json())

                backup_list.append(idnumber_sikola)
                save_backup_list(backup_list)
                
        with open(f"data/User/{backupnama}.json","w",) as f: json.dump(errorMhs, f, indent=4)



if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
