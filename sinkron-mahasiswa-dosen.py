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


def save_backup_list(backup_list, filename="log/backup_list_enrol_user.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/backup_list_enrol_user.pkl"):
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


kelasActiveName = "TA232.1"
listDataDetailKelasFile = glob.glob(f"data/detailkelas/{kelasActiveName}/*.json")
baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
verify_ssl = False

loopingSize = len(listDataDetailKelasFile)
currentFile = 0
for filePath in listDataDetailKelasFile:
    currentFile += 1
    with open(filePath, "r") as f:
        data = f.read()

    dataDetailCourse = json.loads(data)
    idnumber_sikola = dataDetailCourse["idnumber_sikola"]
    shortname_sikola = dataDetailCourse["shortname_sikola"]
    mahasiswas = dataDetailCourse["mahasiswas"]
    
    print(f"Progress: {((currentFile / loopingSize) * 100):.2f} %")
    if idnumber_sikola not in backup_list:
        print(f"Shortname Course : {shortname_sikola}")

        paramsAPIGetCourseByField = {
            "wsfunction": "core_course_get_courses_by_field",
            "field": "idnumber",
            "value": idnumber_sikola,
        }

        responseGetCourseSikolaByField = requests.get(
            baseUrl, params=paramsAPIGetCourseByField, verify=verify_ssl
        )

        if responseGetCourseSikolaByField.status_code == 200:
            dataCourseSikola = responseGetCourseSikolaByField.json()

            for student in mahasiswas:
                paramsAPIGetUserSikolaByField = {
                    "wsfunction": "core_user_get_users_by_field",
                    "field": "username",
                    "values[0]": student["nim"].lower(),
                }

                responseGetUserSikolaByField = requests.get(
                    baseUrl, params=paramsAPIGetUserSikolaByField, verify=verify_ssl
                )

                if responseGetUserSikolaByField.status_code == 200:
                    dataUserSikola = responseGetUserSikolaByField.json()
                    if len(dataUserSikola) == 0:
                        paramsAPICreateUserSikolaByField = {
                            "wsfunction": "core_user_create_users",
                            "users[0][firstname]":student["nama_mahasiswa"],
                            "users[0][username]": student["nim"].lower(),
                            "users[0][idnumber]": student["nim"].lower(),
                            "users[0][password]": f"{student["nim"].lower()}@2023!",
                            'users[0][lastname]':'.',
                            'users[0][email]':f"{student["nim"].lower()}@unhas.ac.id"
                        }

                        responseGetCreateUserSikolaByField = requests.get(
                            baseUrl, params=paramsAPICreateUserSikolaByField, verify=verify_ssl
                        )
                        if responseGetCreateUserSikolaByField.status_code == 200:
                            dataUserBaruSikola = responseGetCreateUserSikolaByField.json()

                            paramsAPIEnrollUserSikolaByField = {
                                "wsfunction": "enrol_manual_enrol_users",
                                "enrolments[0][roleid]": 5,
                                "enrolments[0][userid]": dataUserBaruSikola[0]['id'],
                                'enrolments[0][courseid]':dataCourseSikola['courses'][0]['id'],
                            }

                            responseEnrollUserSikolaByField = requests.get(
                                baseUrl, params=paramsAPIEnrollUserSikolaByField, verify=verify_ssl
                            )
                            if responseEnrollUserSikolaByField.status_code == 200:
                                dataEnrollUser = responseEnrollUserSikolaByField.json()
                                # print(f'New User Created & Enrolled:{dataEnrollUser}')
                            else:
                                print(f"Error: {responseEnrollUserSikolaByField.status_code}")
                                print(responseEnrollUserSikolaByField.text)

                        else:
                            print(f"Error: {responseGetCreateUserSikolaByField.status_code}")
                            print(responseGetCreateUserSikolaByField.text)
                    else:
                        paramsAPIEnrollUserSikolaByField = {
                            "wsfunction": "enrol_manual_enrol_users",
                            "enrolments[0][roleid]": 5,
                            "enrolments[0][userid]": dataUserSikola[0]['id'],
                            'enrolments[0][courseid]':dataCourseSikola['courses'][0]['id'],
                        }

                        responseEnrollUserSikolaByField = requests.get(
                            baseUrl, params=paramsAPIEnrollUserSikolaByField, verify=verify_ssl
                        )
                        if responseEnrollUserSikolaByField.status_code == 200:
                            dataEnrollUser = responseEnrollUserSikolaByField.json()
                            # print(f'Enrol User:{dataEnrollUser}')
                        else:
                            print(f"Error: {responseEnrollUserSikolaByField.status_code}")
                            print(responseEnrollUserSikolaByField.text)
                else:
                    print(f"Error: {responseGetUserSikolaByField.status_code}")
                    print(responseGetUserSikolaByField.text)

            backup_list.append(idnumber_sikola)
            save_backup_list(backup_list)


        else:
            print(f"Error: {responseGetCourseSikolaByField.status_code}")
            print(responseGetCourseSikolaByField.text)
