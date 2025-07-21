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

backupnama = "enrollcreateDOSEN-MAR03-TA242"

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

async def enroll_user_and_group(session, lectrurers, baseUrl, courseData, errorDosens, dosenCreate):
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
            dosenGroups = next(
                (group for group in dataCourseGroup if group["name"] == "DOSEN"), None
            )
            
            if dosenGroups:
                dosenGroupsId = dosenGroups["id"]

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
                enrolledDosens = set()
                # dosenIdnumber = set(lecturer["nip"].lower() for lecturer in lectrurers)
                dosenIdnumber = set(int(lecturer["id"]) for lecturer in lectrurers)

                for peserta in dataPeserta:
                    nip_dosen = peserta["username"].lower()
                    
                    if any(role["roleid"] == 3 for role in peserta["roles"]):
                        idnumber = peserta.get('idnumber')
                        
                        if idnumber is not None and idnumber.isnumeric():
                            idnumber = int(peserta.get('idnumber'))
                            id_number_dosen = int(peserta["idnumber"])
                            # if id_number_dosen not in dosenIdnumber:
                            #     paramsAPIUnenrollUserSikolaByField = {
                            #         "wsfunction": "enrol_manual_unenrol_users",
                            #         "enrolments[0][userid]": peserta["id"],
                            #         'enrolments[0][courseid]': course_id,
                            #     }
                            #     tasks.append(
                            #         session.get(baseUrl, params=paramsAPIUnenrollUserSikolaByField, ssl=False)
                            #     )
                            #     print('UNENROLL DOSEN', nip_dosen)
                            
                            if 'groups' in peserta and any(group["name"] == "DOSEN" for group in peserta["groups"]):
                                enrolledDosens.add(int(peserta["idnumber"]))
                            else:
                                errorDosens.append(peserta['username'])

                # Loop untuk setiap student
                
                for lecturer in lectrurers:
                    nip_dosens = lecturer["nip"].lower()
                    id_number_dosens = int(lecturer["id"])
                    try:   
                        if id_number_dosens not in enrolledDosens:
                            paramsAPIGetUserSikolaByFieldUpdate = {
                                "wsfunction": "core_user_get_users_by_field",
                                "field": "idnumber",
                                "values[0]": id_number_dosens,
                            }
                            
                            async with session.get(
                                baseUrl, params=paramsAPIGetUserSikolaByFieldUpdate, ssl=False
                            ) as responseGetUserSikolaByField:
                                dataUserSikola = await responseGetUserSikolaByField.json()
                    
                            if len(dataUserSikola) == 0:
                                # Jika pengguna belum ada, buat akun
                                email = f"{nip_dosens}@unhas.ac.id"
                                paramsAPICreateUserSikolaByField = {
                                    "wsfunction": "core_user_create_users",
                                    "users[0][firstname]": '.',
                                    "users[0][username]": nip_dosens,
                                    "users[0][password]": nip_dosens,
                                    "users[0][idnumber]": id_number_dosens,
                                    'users[0][lastname]': lecturer["nama"],
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
                                    "enrolments[0][roleid]": 3,
                                    "enrolments[0][userid]": dataUserBaruSikola[0]['id'],
                                    'enrolments[0][courseid]': course_id,
                                    "enrolments[0][timestart]": 1737302400,
                                }
                                tasks.append(
                                    session.get(baseUrl, params=paramsAPIEnrollUserSikolaByFieldCreate, ssl=False)
                                )
                                
                                paramsAPIEnrollMahasiswaToGroupCreate = {
                                    "wsfunction": "core_group_add_group_members",
                                    "members[0][groupid]": dosenGroupsId,
                                    "members[0][userid]": dataUserBaruSikola[0]['id'],
                                }
                                
                                tasks.append(
                                    session.get(baseUrl, params=paramsAPIEnrollMahasiswaToGroupCreate, ssl=False)
                                )
                                dosenCreate.append({
                                    'nip': nip_dosens,
                                    'nama_dosen': lecturer["nama"],
                                    'id_user_sikola' : dataUserBaruSikola[0]['id'],
                                    'id_user_neosia' : id_number_dosens
                                })

                                
                                
                            else:
                                # Jika pengguna sudah ada
                                userId = dataUserSikola[0]['id']
                                print('UPDATE ENROll DOSEN', dataUserSikola[0]['username'])

                            # Enroll user ke course
                                paramsAPIEnrollUserSikolaByField = {
                                    "wsfunction": "enrol_manual_enrol_users",
                                    "enrolments[0][roleid]": 3,
                                    "enrolments[0][userid]": userId,
                                    'enrolments[0][courseid]': course_id,
                                    "enrolments[0][timestart]": 1737302400,

                                }
                                tasks.append(
                                    session.get(baseUrl, params=paramsAPIEnrollUserSikolaByField, ssl=False)
                                )
                                
                                
                                paramsUpdate = {
                                    "wsfunction": "core_user_update_users",
                                    "users[0][id]": userId,
                                    "users[0][idnumber]": lecturer["id"]
                                }
                                tasks.append(
                                    session.get(baseUrl, params=paramsUpdate, ssl=False)
                                )

                                # Enroll user ke grup MAHASISWA
                                paramsAPIEnrollMahasiswaToGroup = {
                                    "wsfunction": "core_group_add_group_members",
                                    "members[0][groupid]": dosenGroupsId,
                                    "members[0][userid]": userId,
                                }
                                tasks.append(
                                    session.get(baseUrl, params=paramsAPIEnrollMahasiswaToGroup, ssl=False)
                                )
                            
                        
                    except Exception as e:
                        print(f"Error processing READY DOSEN {lecturer['nip']}: {e}")
                        errorDosens.append(lecturer['nip'])
                        

    
    # else:
    #     for lecturer in lectrurers:
    #         nip_dosens = lecturer["nip"].lower()
    #         id_number_dosens = int(lecturer["id"])

    #         try:   
    #             paramsAPIGetUserSikolaByFieldUpdate = {
    #                 "wsfunction": "core_user_get_users_by_field",
    #                 "field": "idnumber",
    #                 "values[0]": id_number_dosens,
    #             }
                
    #             async with session.get(
    #                 baseUrl, params=paramsAPIGetUserSikolaByFieldUpdate, ssl=False
    #             ) as responseGetUserSikolaByField:
    #                 dataUserSikola = await responseGetUserSikolaByField.json()
        
    #             if len(dataUserSikola) == 0:
    #                 email = f"{nip_dosens}@unhas.ac.id"
    #                 paramsAPICreateUserSikolaByField = {
    #                     "wsfunction": "core_user_create_users",
    #                     "users[0][firstname]": ".",
    #                     "users[0][username]": nip_dosens,
    #                     "users[0][password]": nip_dosens,
    #                     "users[0][idnumber]": lecturer["id"],
    #                     'users[0][lastname]': lecturer["nama"],
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
    #                 "users[0][idnumber]": lecturer["id"]
    #             }
    #             tasks.append(
    #                 session.get(baseUrl, params=paramsUpdate, ssl=False)
    #             )

    #         except Exception as e:
    #             print(f"Error processing NONE DOSEN {lecturer['nip']}: {e}")
   
   
    return tasks





async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        # kelasActiveName = "TEST"
        kelasActiveName = "TA242.7"
        listDataDetailKelasFile = glob.glob(
            f"data/detailkelas/{kelasActiveName}/*.json"
        )
        # baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=4a91b2ebcb33cfb3f24d2678b2e214df&moodlewsrestformat=json"

        loopingSize = len(listDataDetailKelasFile)
        currentFile = 0
        
        task = []
        errorDosens =[]
        dosenCreate =[]
        
        dosens = []

        for filePath in listDataDetailKelasFile:
            currentFile += 1
            with open(filePath, "r", encoding="utf-8") as f:
                data = f.read()

            dataDetailCourse = json.loads(data)

            idnumber_sikola = dataDetailCourse["idnumber_sikola"]
            shortname_sikola = dataDetailCourse["shortname_sikola"]
            dosens = dataDetailCourse["dosens"]
            koordinators = dataDetailCourse["koordinators"]
            
            for koordinator in koordinators:
                if 'dosen' in koordinator:
                    koordinatorDosen = koordinator['dosen']
                    dosens.append({
                        'deleted_at': koordinatorDosen.get('deleted_at'),
                        'id': koordinatorDosen.get('id'),
                        'id_user': koordinatorDosen.get('id_user'),
                        'id_prodi': koordinatorDosen.get('id_prodi'),
                        'nama': koordinatorDosen.get('nama'),
                        'nidn': koordinatorDosen.get('nidn'),
                        'nip': koordinatorDosen.get('nip'),
                        'is_active': koordinatorDosen.get('is_active'),
                        'updated_by': koordinatorDosen.get('updated_by'),
                        'id_registrasi_pddikti': koordinatorDosen.get('id_registrasi_pddikti'),
                        'pivot': {
                            'id_kelas_kuliah': koordinator.get('id_kelas_kuliah'),
                            'id_dosen': koordinatorDosen.get('id'),
                        },
                    })
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

                task = await enroll_user_and_group(
                    session, dosens, baseUrl, dataCourseSikola, errorDosens, dosenCreate
                )
                
                print(idnumber_sikola, 'ID NUMBER')

                respnsesTask = await asyncio.gather(*task)

                for res in respnsesTask:
                    resultFetch.append(await res.json())

                backup_list.append(idnumber_sikola)
                save_backup_list(backup_list)
        with open(f"data/User/{backupnama}.json","w",) as f: json.dump(errorDosens, f, indent=4)
        with open(f"data/User/{backupnama}-dosenCreate.json","w",) as f: json.dump(dosenCreate, f, indent=4)



if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
