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


def save_backup_list(backup_list, filename="log/list_new_course-from-v4-D.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/list_new_course-from-v4-D.pkl"):
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


async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        kelasActiveNameNewVer = "TA232.11"
        listDataDetailKelasFileNewVer = glob.glob(
            f"data/detailkelas/{kelasActiveNameNewVer}/*.json"
        )

        currentFile = 0
        listCourseStudentChange = []

        for filePath in listDataDetailKelasFileNewVer:
            shortnameSikola = f"TA232-{filePath.split("/")[3].replace(".json", "")}"

            if shortnameSikola == 'TA232-120037':
                itemDataChange = []

                with open(filePath, "r") as f:
                    dataNew = f.read()

                dataDetailCourseNew = json.loads(dataNew)
                dosensNew = dataDetailCourseNew["dosens"]

                idnumber_sikola = dataDetailCourseNew["idnumber_sikola"]
                itemDataChange.append(idnumber_sikola)
                itemDataChange.append(filePath)

                outM = []
                inM = []

                # FINDING IN STUDENTS
                for mNew in dosensNew:
                    inM.append(mNew)

                itemDataChange.append(outM)
                itemDataChange.append(inM)

                listCourseStudentChange.append(itemDataChange)

                with open(
                    f"data/detailkelas/ChangeItem/dosen/{shortnameSikola}.json", "w"
                ) as json_file:
                    json.dump(listCourseStudentChange, json_file)


# get fetch_sikola_course()
if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
