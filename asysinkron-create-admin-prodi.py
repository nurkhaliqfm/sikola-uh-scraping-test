import aiohttp
import asyncio
import glob
import os
import requests
import json
import pickle
import csv

from dotenv import load_dotenv

load_dotenv()

# Disable InsecureRequestWarning
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def save_backup_list(backup_list, filename="log/backup_list_create_admin_prodi-v2.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/backup_list_create_admin_prodi-v2.pkl"):
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


async def create_admin_prodi(session, admins, baseUrl):
    task = []
    found = 0
    notfound = 0
    for admin in admins:
        usernameAdmin = admin[0].strip()
        firstnameAdmin = admin[1].strip()
        emailAdmin = admin[3].strip()

        if usernameAdmin not in backup_list:
            if not usernameAdmin == "username":
                paramsAPIGetUserSikolaByField = {
                    "wsfunction": "core_user_get_users_by_field",
                    "field": "username",
                    "values[0]": usernameAdmin,
                }

                responseGetUserSikolaByField = await session.get(
                    baseUrl, params=paramsAPIGetUserSikolaByField, ssl=False
                )

                dataUserSikola = await responseGetUserSikolaByField.json()

                if len(dataUserSikola) == 0:
                    notfound += 1
                    print(f"Create User {firstnameAdmin}")
                    paramsAPICreateUserSikolaByField = {
                        "wsfunction": "core_user_create_users",
                        "users[0][firstname]": firstnameAdmin,
                        "users[0][username]": usernameAdmin,
                        "users[0][idnumber]": usernameAdmin,
                        "users[0][password]": f"{usernameAdmin}@2023!",
                        "users[0][lastname]": "-",
                        "users[0][email]": usernameAdmin,
                    }

                    responseGetCreateUserSikolaByField = await session.get(
                        baseUrl, params=paramsAPICreateUserSikolaByField, ssl=False
                    )

                    dataUserBaruSikola = await responseGetCreateUserSikolaByField.json()
                    print(paramsAPICreateUserSikolaByField)
                else:
                    found += 1
                    # print(f"User : {firstnameAdmin} FOUND")

                # backup_list.append(usernameAdmin)
                # save_backup_list(backup_list)

    print(f"Found = {found}")
    print(f"Not Found = {notfound}")
    return task


async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        # baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=2733cd661f599f6dcb60629ea3248f8c&moodlewsrestformat=json"

        with open("data/admin-prodi-v2.csv", "r") as file:
            dataCSVAdminProdi = csv.reader(file, delimiter=",")

            task = await create_admin_prodi(session, dataCSVAdminProdi, baseUrl)
            respnsesTask = await asyncio.gather(*task)

            for res in respnsesTask:
                resultFetch.append(await res.json())


if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
