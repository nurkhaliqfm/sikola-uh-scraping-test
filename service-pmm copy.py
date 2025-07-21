import aiohttp
import asyncio
import glob
import os
import requests
import json
import pickle
import csv
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Disable InsecureRequestWarning
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# def save_backup_list(
#     backup_list, filename="log/backup_list_enrol_mahasiswa-enrole-inbound.pkl"
# ):
#     with open(filename, "wb") as file:
#         pickle.dump(backup_list, file)


# def load_backup_list(filename="log/backup_list_enrol_mahasiswa-enrole-inbound.pkl"):
#     try:
#         with open(filename, "rb") as file:
#             return pickle.load(file)
#     except FileNotFoundError:
#         return None


# backup_list = load_backup_list()

# if backup_list is None:
#     backup_list = list([])
#     save_backup_list(backup_list)
# else:
#     print("Backup list loaded successfully.")


resultFetch = []



async def buat_course(session, course, baseUrl):
    tasks = []
    
    print(course['kelas'])

    for kelas in course['kelas']:
        try:
            id_kelas = kelas['kelas_id']
            nama_kelas = kelas['kelas_nama'].upper()
    
            shortname = f"TA241-{nama_kelas} [{id_kelas}]"
            
            print(shortname)

            
            paramsAPIGetCourseByField = {
                "wsfunction": "core_course_get_courses_by_field",
                "field": "shortname",
                "value": shortname,
            }
            
            async with session.get(baseUrl, params=paramsAPIGetCourseByField, ssl=False) as responseGetCourseSikolaByField:
                dataCourseSikola = await responseGetCourseSikolaByField.json()
                
            
            if 'courses' in dataCourseSikola and len(dataCourseSikola['courses']) > 0:
                course_id = dataCourseSikola['courses'][0]['id']
                print(course_id)
                
                paramsAPIGetCourseGroup = {
                    "wsfunction": "core_group_get_course_groups",
                    "courseid": course_id,
                }

                responseGETCourseGroup = await session.get(baseUrl, params=paramsAPIGetCourseGroup, ssl=False)
                dataCourseGroup = await responseGETCourseGroup.json()

                if dataCourseGroup:
                    mahasiswaGroup = next((group for group in dataCourseGroup if group["name"] == "MAHASISWA"), None)
                    
                    if mahasiswaGroup:
                        mahasiswaGroupId = mahasiswaGroup["id"]

                        getUserPeserta = {
                            "wsfunction": "core_enrol_get_enrolled_users",
                            "courseid": course_id,
                        }

                        responseGetPeserta = await session.get(baseUrl, params=getUserPeserta, ssl=False)
                        dataPeserta = await responseGetPeserta.json()

                        enrolledNIMs = set()
                        userId = None


                        for peserta in dataPeserta:
                            username_lower = peserta["username"].lower()
                            if 'groups' in peserta and any(group["name"] == "MAHASISWA" for group in peserta["groups"]):
                                enrolledNIMs.add(peserta["username"])

                        nim_lower = course['nim_tamu'].lower()
                        nim_upper = course['nim_tamu'].upper()
                        nama_mhs = course['nama_lengkap'].upper()

                        try:   
                            if nim_lower not in enrolledNIMs:
                                paramsAPIGetUserSikolaByFieldUpdate = {
                                    "wsfunction": "core_user_get_users_by_field",
                                    "field": "username",
                                    "values[0]": nim_lower,
                                }
                                
                                async with session.get(baseUrl, params=paramsAPIGetUserSikolaByFieldUpdate, ssl=False) as responseGetUserSikolaByField:
                                    dataUserSikola = await responseGetUserSikolaByField.json()
                        
                                if len(dataUserSikola) == 0:
                                    email = f"{nim_lower}-pmm@unhas.ac.id"
                                    paramsAPICreateUserSikolaByField = {
                                        "wsfunction": "core_user_create_users",
                                        "users[0][firstname]": nim_upper,
                                        "users[0][username]": nim_lower,
                                        "users[0][password]": nim_lower,
                                        "users[0][idnumber]": nim_lower,
                                        'users[0][lastname]': nama_mhs,
                                        'users[0][email]': email,
                                    }
                                    
                                    responseGetCreateDosenSikolaByFieldCreate = await session.get(
                                        baseUrl, params=paramsAPICreateUserSikolaByField, ssl=False
                                    )
                                    
                                    dataUserBaruSikola = await responseGetCreateDosenSikolaByFieldCreate.json()

                                    userId = dataUserBaruSikola[0]['id']
                                    print('CREATE USER', dataUserBaruSikola[0]['username'])
                                    paramsAPIEnrollUserSikolaByFieldCreate = {
                                        "wsfunction": "enrol_manual_enrol_users",
                                        "enrolments[0][roleid]": 5,
                                        "enrolments[0][userid]": dataUserBaruSikola[0]['id'],
                                        'enrolments[0][courseid]': course_id,
                                    }
                                    tasks.append(
                                        session.get(baseUrl, params=paramsAPIEnrollUserSikolaByFieldCreate, ssl=False)
                                    )
                                    
                                    paramsAPIEnrollMahasiswaToGroupCreate = {
                                        "wsfunction": "core_group_add_group_members",
                                        "members[0][groupid]": mahasiswaGroupId,
                                        "members[0][userid]": dataUserBaruSikola[0]['id'],
                                    }
                                    
                                    tasks.append(
                                        session.get(baseUrl, params=paramsAPIEnrollMahasiswaToGroupCreate, ssl=False)
                                    )
                                    
                                else:
                                    userId = dataUserSikola[0]['id']
                                    print('UPDATE ENROLL USER', dataUserSikola[0]['username'])

                                    paramsAPIEnrollUserSikolaByField = {
                                        "wsfunction": "enrol_manual_enrol_users",
                                        "enrolments[0][roleid]": 5,
                                        "enrolments[0][userid]": userId,
                                        'enrolments[0][courseid]': course_id,
                                    }
                                    tasks.append(
                                        session.get(baseUrl, params=paramsAPIEnrollUserSikolaByField, ssl=False)
                                    )
                                    
                                    paramsUpdate = {
                                        "wsfunction": "core_user_update_users",
                                        "users[0][id]": userId,
                                        "users[0][idnumber]": nim_lower
                                    }
                                    tasks.append(
                                        session.get(baseUrl, params=paramsUpdate, ssl=False)
                                    )

                                    paramsAPIEnrollMahasiswaToGroup = {
                                        "wsfunction": "core_group_add_group_members",
                                        "members[0][groupid]": mahasiswaGroupId,
                                        "members[0][userid]": userId,
                                    }
                                    tasks.append(
                                        session.get(baseUrl, params=paramsAPIEnrollMahasiswaToGroup, ssl=False)
                                    )
                            
                        except Exception as e:
                            print(f"Error processing student {nim_lower}: {e}")
                        for enrolled_nim in enrolledNIMs:
                                if enrolled_nim != nim_lower and enrolled_nim.startswith("t"):
                                    if userId is not None:
                                        paramsAPIUnenrollUser = {
                                            "wsfunction": "enrol_manual_unenrol_users",
                                            "enrolments[0][userid]": userId,
                                            "enrolments[0][courseid]": course_id,
                                        }
                                        tasks.append(
                                            session.get(baseUrl, params=paramsAPIUnenrollUser, ssl=False)
                                        )
                                        print(f"Unenrolled user {enrolled_nim} {userId} from course {course_id}")
                                    
                                    
                                    else:
                                        print(f"not unenroll user {enrolled_nim} as userId is None")
                                

        except ValueError as e:
            print(f"Error processing class {kelas['kelas_id']}: {e}")

    if tasks:
        await asyncio.gather(*tasks)
    
# async def fetch_data_from_service():
#     token = "a1a67ee53c30551db30146b3d6bf5f4d83512b572a56fce3d60d7dff7085de625d"  # Ganti dengan token yang sesuai
#     url = "https://neosipakatau.unhas.ac.id/home/datatosikola"
    
#     async with aiohttp.ClientSession() as session:
#         headers = {
#             "Content-Type": "multipart/form-data"
#         }
#         body = {
#             "token": token
#         }
#         form_data = aiohttp.FormData()
#         form_data.add_field('token', token)
#         async with session.post(url, data=form_data, ssl=False) as response:
#             response_data = await response.json()
#             return response_data['data']

async def main():
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"
    
    # data = await fetch_data_from_service()

    async with aiohttp.ClientSession() as session:
        tasks = []
        print("Processing Course")

        # Get data from external service
        url = "https://neosipakatau.unhas.ac.id/home/datatosikola"
        token = "a1a67ee53c30551db30146b3d6bf5f4d83512b572a56fce3d60d7dff7085de625d"

        # Menggunakan `form-data` untuk mengirim token
        form_data = aiohttp.FormData()
        form_data.add_field('token', token)

        async with session.post(url, data=form_data, ssl=False) as response:
            # Cek jika response content-type adalah HTML, mungkin terjadi error
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' in content_type:
                # Print atau log HTML untuk debugging
                html_content = await response.text()
                print("Received HTML response, something went wrong:", html_content)
            elif response.status == 200:
                try:
                    responseData = await response.json()
                    data = responseData.get("data", [])

                    for course in data:
                        # print(course)
                        tasks.append(buat_course(session, course, baseUrl))
                except aiohttp.ContentTypeError as e:
                    print("Failed to decode JSON:", e)
            else:
                print("Failed to fetch data from service, status code:", response.status)

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
