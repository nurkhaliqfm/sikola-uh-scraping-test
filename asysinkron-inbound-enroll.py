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


def save_backup_list(
    backup_list, filename="log/backup_list_enrol_mahasiswa-enrole-inbound.pkl"
):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/backup_list_enrol_mahasiswa-enrole-inbound.pkl"):
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


# async def unenroll_user(session, student, baseUrl, courseData):
#     task = []

#     print(f"Student: {student}")
#     paramsAPIGetUserSikolaByField = {
#         "wsfunction": "core_user_get_users_by_field",
#         "field": "username",
#         "values[0]": student.lower(),
#     }

#     responseGetUserSikolaByField = await session.get(
#         baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
#     )

#     dataUserSikola = await responseGetUserSikolaByField.json()
#     print(dataUserSikola)

#     paramsAPIEnrollUserSikolaByField = {
#         "wsfunction": "enrol_manual_enrol_users",
#         "enrolments[0][roleid]": 5,
#         "enrolments[0][userid]": dataUserSikola[0]["id"],
#         "enrolments[0][courseid]": courseData["courses"][0]["id"],
#     }

#     task.append(
#         session.get(baseUrl, params=paramsAPIEnrollUserSikolaByField, ssl=False)
#     )
#     print("Student Done...")

#     return task


# async def fetch_sikola_course_users():
#     async with aiohttp.ClientSession() as session:
#         baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
#         # baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=5efd77a7277c9ef1dc42a29cb812b552&moodlewsrestformat=json"

#         with open("data/DataExternal/data-kelas-inbound.csv", "r") as file:
#             dataChangeFile = csv.reader(file, delimiter=",")

#             # logCourseChange = json.loads(dataChangeFile)

#             # loopingSize = len(dataChangeFile)
#             # currentFile = 0

#             for itemCourse in dataChangeFile:
#                 # currentFile += 1
#                 if not itemCourse[0] == "nim":
#                     print(itemCourse)
#                     shortname = f"TA241-{itemCourse[2]}"

#                     # print(f"Progress: {((currentFile / loopingSize) * 100):.2f} %")

#                     if itemCourse[2] not in backup_list:
#                         print(f"Shortname Course : {shortname}")

#                         paramsAPIGetCourseByField = {
#                             "wsfunction": "core_course_get_courses_by_field",
#                             "field": "shortname",
#                             "value": shortname,
#                         }

#                         responseGetCourseSikolaByField = await session.get(
#                             baseUrl, params=paramsAPIGetCourseByField, ssl=False
#                         )

#                         dataCourseSikola = await responseGetCourseSikolaByField.json()

#                         task = await unenroll_user(
#                             session,
#                             itemCourse[0],
#                             baseUrl,
#                             dataCourseSikola,
#                         )
#                         respnsesTask = await asyncio.gather(*task)

#                         for res in respnsesTask:
#                             resultFetch.append(await res.json())

#                 # backup_list.append(idnumber_sikola)
#                 # save_backup_list(backup_list)
#                 # break




# async def buat_user_pmm(session, student):
    
#     print(student[0])
    
#     nim_lower = student[0].lower()       

    
    
    
#     paramsAPIGetUserSikolaByFieldUpdate = {
#         "wsfunction": "core_user_get_users_by_field",
#         "field": "username",
#         "values[0]": nim_lower,
#     }
    
#     async with session.get(
#         baseUrl, params=paramsAPIGetUserSikolaByFieldUpdate, ssl=False
#     ) as responseGetUserSikolaByField:
#         dataUserSikola = await responseGetUserSikolaByField.json()
        
    
#     if len(dataUserSikola) == 0:
#         # Jika pengguna belum ada, buat akun
#         email = f"{nim_lower}@pmm.unhas.ac.id"
#         paramsAPICreateUserSikolaByField = {
#             "wsfunction": "core_user_create_users",
#             "users[0][firstname]": student[0].upper(),
#             "users[0][username]": nim_lower,
#             "users[0][password]": nim_lower,
#             "users[0][idnumber]": student[0],
#             'users[0][lastname]': student[1].upper(),
#             'users[0][email]': email,
#         }
        
#         responseGetCreateDosenSikolaByFieldCreate = await session.get(
#             baseUrl, params=paramsAPICreateUserSikolaByField, ssl=False
#         )
        
#         dataUserBaruSikola = await responseGetCreateDosenSikolaByFieldCreate.json()


#         # async with session.get(
#         #     baseUrl, params=paramsAPICreateUserSikolaByField, ssl=False
#         # ) as responseGetCreateUserSikolaByField:
#         #     dataUserBaruSikola = await responseGetCreateUserSikolaByField.json()

#         userId = dataUserBaruSikola[0]['id']
#         print('CREATE USER', dataUserBaruSikola[0]['username'])
#         paramsAPIEnrollUserSikolaByFieldCreate = {
#             "wsfunction": "enrol_manual_enrol_users",
#             "enrolments[0][roleid]": 5,
#             "enrolments[0][userid]": dataUserBaruSikola[0]['id'],
#             'enrolments[0][courseid]': course_id,
#         }
#         tasks.append(
#             session.get(baseUrl, params=paramsAPIEnrollUserSikolaByFieldCreate, ssl=False)
#         )
        
#         paramsAPIEnrollMahasiswaToGroupCreate = {
#             "wsfunction": "core_group_add_group_members",
#             "members[0][groupid]": mahasiswaGroupId,
#             "members[0][userid]": dataUserBaruSikola[0]['id'],
#         }
        
#         tasks.append(
#             session.get(baseUrl, params=paramsAPIEnrollMahasiswaToGroupCreate, ssl=False)
#         )
                                
                         
   
#     # try:
    
#     #     for date_obj in range((end_date_obj - start_date_obj).days + 1):
#     #         current_date = (start_date_obj + timedelta(days=date_obj)).strftime("%Y-%m-%d")
#     #         shortname_sikola = f"TA232-{itemClassError[1]}"
        
#     #         paramsAPIGetCourseByField = {
#     #             "wsfunction": "core_course_get_courses_by_field",
#     #             "field": "shortname",
#     #             "value": shortname_sikola,
#     #         }

#     #         responseGetCourseSikolaByField = await session.get(
#     #             baseUrl, params=paramsAPIGetCourseByField, ssl=False
#     #         )

#     #         dataCourseSikola = await responseGetCourseSikolaByField.json()
#     #         tasks.append(attendance_item_raw(session, baseUrl, dataCourseSikola, itemClassError[1], current_date))
        
#     #     await asyncio.gather(*tasks)
        
#     # except Exception as e:
#     #     print(f"{itemClassError[1]}-{itemClassError[0]} : {e}")



async def buat_course(session, course, baseUrl):
    tasks= []
    
    if pd.notna(course.iloc[2]):
        try:
            # Extract the integer part of the number
            # id_kelas = int(course.iloc[5])
            # nama_kelas = course.iloc[6].upper()
            
            # TA241-CORPORATE GOVERMENCE DAN CSR KELAS A [137725]
    
            # shortname = f"TA241-{nama_kelas} [{id_kelas}]"
            idnumber = f"2408.24.24127"
            
            paramsAPIGetCourseByField = {
                "wsfunction": "core_course_get_courses_by_field",
                "field": "idnumber",
                "value": idnumber,
            }
            
            async with session.get(
                    baseUrl, params=paramsAPIGetCourseByField, ssl=False
                ) as responseGetCourseSikolaByField:
                    dataCourseSikola = await responseGetCourseSikolaByField.json()
            if 'courses' in dataCourseSikola and len(dataCourseSikola['courses']) > 0:
                course_id = dataCourseSikola['courses'][0]['id']
                
                print(course_id)
                
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
                        

                        for peserta in dataPeserta:
                            # username_lower = peserta["username"].lower()
                            
                              
                            if 'groups' in peserta and any(group["name"] == "MAHASISWA" for group in peserta["groups"]):
                                enrolledNIMs.add(peserta["username"])

                        # Loop untuk setiap student
                        
                        erroMhs = []

                        nim_lower = course.iloc[2].lower()       
                        nim_upper = course.iloc[2].upper()       
                        nama_mhs = course.iloc[1].upper()   
                        
                        print(course_id, nama_mhs, nim_lower)    
                        try:
                            
                            # paramsAPIGetUserSikolaByFieldUpdate = {
                            #         "wsfunction": "core_user_get_users_by_field",
                            #         "field": "username",
                            #         "values[0]": nim_lower,
                            # }
                                
                            # async with session.get(
                            #     baseUrl, params=paramsAPIGetUserSikolaByFieldUpdate, ssl=False
                            # ) as responseGetUserSikolaByField:
                            #     dataUserSikola = await responseGetUserSikolaByField.json()
                            # userId = dataUserSikola[0]['id']

                    
                            # paramsAPIEnrollUserSikolaByField = {
                            #     "wsfunction": "enrol_manual_enrol_users",
                            #     "enrolments[0][roleid]": 3,
                            #     "enrolments[0][userid]": userId,
                            #     'enrolments[0][courseid]': course_id,
                            # }
                            # tasks.append(
                            #     session.get(baseUrl, params=paramsAPIEnrollUserSikolaByField, ssl=False)
                            # )
                            
                            
                            # paramsUpdate = {
                            #     "wsfunction": "core_user_update_users",
                            #     "users[0][id]": userId,
                            #     "users[0][idnumber]": nim_lower
                            # }
                            # tasks.append(
                            #     session.get(baseUrl, params=paramsUpdate, ssl=False)
                            # )

                            # # Enroll user ke grup MAHASISWA
                            # paramsAPIEnrollMahasiswaToGroup = {
                            #     "wsfunction": "core_group_add_group_members",
                            #     "members[0][groupid]": mahasiswaGroupId,
                            #     "members[0][userid]": userId,
                            # }
                            # tasks.append(
                            #     session.get(baseUrl, params=paramsAPIEnrollMahasiswaToGroup, ssl=False)
                            # )
                            if nim_lower not in enrolledNIMs:
                                paramsAPIGetUserSikolaByFieldUpdate = {
                                    "wsfunction": "core_user_get_users_by_field",
                                    "field": "username",
                                    "values[0]": nim_lower,
                                }
                                
                                async with session.get(
                                    baseUrl, params=paramsAPIGetUserSikolaByFieldUpdate, ssl=False
                                ) as responseGetUserSikolaByField:
                                    dataUserSikola = await responseGetUserSikolaByField.json()
                        
                                if len(dataUserSikola) == 0:
                                    # Jika pengguna belum ada, buat akun
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
                                    # Jika pengguna sudah ada
                                    userId = dataUserSikola[0]['id']
                                    print('UPDATE ENROll USER', dataUserSikola[0]['username'])

                                # Enroll user ke course
                                    paramsAPIEnrollUserSikolaByField = {
                                        "wsfunction": "enrol_manual_enrol_users",
                                        "enrolments[0][roleid]": 3,
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

                                    # Enroll user ke grup MAHASISWA
                                    paramsAPIEnrollMahasiswaToGroup = {
                                        "wsfunction": "core_group_add_group_members",
                                        "members[0][groupid]": mahasiswaGroupId,
                                        "members[0][userid]": userId,
                                    }
                                    tasks.append(
                                        session.get(baseUrl, params=paramsAPIEnrollMahasiswaToGroup, ssl=False)
                                    )
                            
                        except Exception as e:
                            print(f"Error processing READY student {nim_lower}: {e}")
                            
            


                        


                    
            
            
        except ValueError as e:
            # Handle the case where conversion to integer fails
            print(f"Error converting {course[5]} to an integer: {e}")
    if tasks:
        await asyncio.gather(*tasks)
    
    
async def initial_excel():
    async with aiohttp.ClientSession() as session:
        tasks = []
        print(f"Processing Course")
        
        if fileDataForm.endswith(".xlsx"):
            df = pd.read_excel(f"data/DataExternal/{fileDataForm}")
            
            for index, row in df.iterrows():
                try:
                    # course = row.to_dict()

                    tasks.append(buat_course(session, row, baseUrl))
                except Exception as e:
                    print(f"{row}-{index} : {e}")
            # unique_ids = df.drop_duplicates(subset=['nim_tamu'])[['nim_tamu', 'nama_lengkap']]

            
            # for index, row in unique_ids.iterrows():
            #     try:
            #         tasks.append(buat_user_pmm(session, row.tolist()))
            #     except Exception as e:
            #             print(f"{row}-{index} : {e}")
          
                                  
        else:
            print("Unsupported file format")

        await asyncio.gather(*tasks)


# get fetch_sikola_course()
if __name__ == "__main__":
    currentDate = "pmm-1"

    kelasActiveName = "TA232.12"
    fileDataForm = "mentor.xlsx"
    
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"

    
    asyncio.run(initial_excel())
