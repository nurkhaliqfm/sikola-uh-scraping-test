import aiohttp
import asyncio
import glob
import os
import requests
import json
import pickle

from dotenv import load_dotenv

load_dotenv()

resultFetch = []


async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        kelasActiveName = "TA231"
        listDataDetailKelasFile = glob.glob(
            f"data/detailkelas/{kelasActiveName}/*.json"
        )
        # baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=2733cd661f599f6dcb60629ea3248f8c&moodlewsrestformat=json"

        loopingSize = len(listDataDetailKelasFile)
        currentFile = 0

        for filePath in listDataDetailKelasFile:
            currentFile += 1
            with open(filePath, "r") as f:
                data = f.read()

            dataDetailCourse = json.loads(data)

            namaProdi = dataDetailCourse["nama_prodi"]

            print(f"Progress: {((currentFile / loopingSize) * 100):.2f} %")

            print(f"Shortname Course : {shortname_sikola}")

            # if shortname_sikola == 'TA232-124999':
            # paramsAPIGetCourseByField = {
            #     "wsfunction": "core_course_get_courses_by_field",
            #     "field": "idnumber",
            #     "value": idnumber_sikola,
            # }

            # responseGetCourseSikolaByField = await session.get(
            #     baseUrl, params=paramsAPIGetCourseByField, ssl=False
            # )

            # dataCourseSikola = await responseGetCourseSikolaByField.json()
            # task = await enroll_user(session, mahasiswas, baseUrl, dataCourseSikola)
            # respnsesTask = await asyncio.gather(*task)

            # for res in respnsesTask:
            #     resultFetch.append(await res.json())

            # backup_list.append(idnumber_sikola)
            # save_backup_list(backup_list)


# get fetch_sikola_course()
if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
