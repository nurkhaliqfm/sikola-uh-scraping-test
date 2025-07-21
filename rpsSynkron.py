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


def save_backup_list(backup_list, filename="log/backup_list_enrol_lecturer-RPS-15Aug.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)


def load_backup_list(filename="log/backup_list_enrol_lecturer-RPS-15Aug.pkl"):
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




async def rps_synkron(session, baseUrlRps, urlRps, dataCourseSikola, sizeUserInCourse, kode_matkul):
    task = []
    
    payload = json.dumps({
        "username": "sikola",
        "password": "@dminSikol4unh@s"
    })
    headers = {
        'Content-Type': 'application/json'
    }
        
    
    loginRps = await session.post(urlRps+"/login", data=payload, headers=headers, ssl=False)
    getToken = await loginRps.json()
            
    tokenRps = getToken['access_token']

    headersLogin = {
        "Authorization": f"Bearer {tokenRps}"
    }

    try:
        async with session.get(
            f"{urlRps}/get_rps/{kode_matkul}",
            headers=headersLogin,
            ssl=False,
        ) as response:
            responseRps = await response.json()
                
            courseId = dataCourseSikola['courses'][0]['id']
            if len(responseRps['rps']) > 0 and len(responseRps['rps'][0]['alur_pembelajaran']) > 0:
                
                for index, rps in enumerate(responseRps['rps'][0]['alur_pembelajaran']):
                    dataPost = {
                        'alurid': rps['alurid'],
                        'pekan': rps['pekan'],
                        'sub_cpmk_ind': rps['sub_cpmk_ind'],
                        'sub_cpmk_eng': rps['sub_spmk_eng'],
                    }
                    
                    insertsection = index
                    
                    # url = f"https://sikola-v2.unhas.ac.id/course/createSectionRps.php?courseId={courseId}&insertsection=0"
                    # headersPost = {
                    #     'Content-Type': 'application/json',
                    #     'Authorization': 'Bearer ccd437b923b46aa49e922034903ac628a447f11f8cf4d464d7d21b790ccc6ab7e88a96fb5b4cee1a87ab1dddb3aea7e3a715ad9f0d9f730de09af7caa56b7a73044ef0a7be7fb15931152f0ecb66f78d1b202f1103d0820ccd445186896062f769a6818bbf1963a6790940b0059e47933637b60aecec366c7c62aebfce7f8e1fsaww',
                    #     'Cookie': 'MoodleSession=skr9jh1v4ei11nmlpn2fj00kl2'
                    # }
                    
                    # payload = json.dumps(dataPost)

                    # try:
                    #     async with session.post(url, headers=headersPost, data=payload, ssl=False) as post_response:
                    #         response_text = await post_response.text()
                    #         print(f"Response for alurid {rps['alurid']}: {response_text}")

                    # except aiohttp.ClientError as e:
                    #     print(f"Request failed for alurid {rps['alurid']}: {e}")

                print(f"Processing RPS for {kode_matkul} complete.")
            else:
                # Create 16 default sections
                for index in range(16):
                    dataPost = {
                        'pekan': index + 1
                    }

                    url = f"https://sikola-v2.unhas.ac.id/course/createSectionRpsDefault.php?courseId={courseId}&insertsection=0"
                    headersPost = {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ccd437b923b46aa49e922034903ac628a447f11f8cf4d464d7d21b790ccc6ab7e88a96fb5b4cee1a87ab1dddb3aea7e3a715ad9f0d9f730de09af7caa56b7a73044ef0a7be7fb15931152f0ecb66f78d1b202f1103d0820ccd445186896062f769a6818bbf1963a6790940b0059e47933637b60aecec366c7c62aebfce7f8e1fsaww',
                        'Cookie': 'MoodleSession=skr9jh1v4ei11nmlpn2fj00kl2'
                    }

                    payload = json.dumps(dataPost)

                    try:
                        async with session.post(url, headers=headersPost, data=payload, ssl=False) as post_response:
                            response_text = await post_response.text()
                            print(f"Response for default section {index + 1}: {response_text}")

                    except aiohttp.ClientError as e:
                        print(f"Response error for default section {index + 1}: {e}")

                print(f"No RPS data found for {kode_matkul}, default sections created.")
                
    
    except Exception as e:
        courseId = dataCourseSikola['courses'][0]['id']

        for index in range(16):
            dataPost = {
                'pekan': index + 1
            }

            url = f"https://sikola-v2.unhas.ac.id/course/createSectionRpsDefault.php?courseId={courseId}&insertsection=0"
            headersPost = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ccd437b923b46aa49e922034903ac628a447f11f8cf4d464d7d21b790ccc6ab7e88a96fb5b4cee1a87ab1dddb3aea7e3a715ad9f0d9f730de09af7caa56b7a73044ef0a7be7fb15931152f0ecb66f78d1b202f1103d0820ccd445186896062f769a6818bbf1963a6790940b0059e47933637b60aecec366c7c62aebfce7f8e1fsaww',
                'Cookie': 'MoodleSession=skr9jh1v4ei11nmlpn2fj00kl2'
            }

            payload = json.dumps(dataPost)

            try:
                async with session.post(url, headers=headersPost, data=payload, ssl=False) as post_response:
                    response_text = await post_response.text()
                    print(f"Response for default section {index + 1}: {response_text}")

            except aiohttp.ClientError as e:
                print(f"Response error for default section {index + 1}: {e}")

    return task

async def fetch_sikola_course_users():
    async with aiohttp.ClientSession() as session:
        kelasActiveName = "TA241.1"
        # kelasActiveName = "TEST"
        listDataDetailKelasFile = glob.glob(
            f"data/detailkelas/{kelasActiveName}/*.json"
        )
        # baseUrl = os.getenv("NEXT_PUBLIC_API_NEOSIKOLA")
        baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"
        
        urlRps = 'https://cpl.unhas.ac.id:8106'
        loopingSize = len(listDataDetailKelasFile)
        currentFile = 0
        
       
        
        urlRps = "https://cpl.unhas.ac.id:8106"
       
        # loginRps = await session.post(urlRps+"/login", data=payload, headers=headers, ssl=False)
        # tokenRps = await loginRps.json()
        
        # tokenRps = tokenRps['access_token']
        
        for filePath in listDataDetailKelasFile:

            currentFile += 1
            with open(filePath, "r", encoding="utf-8") as f:
                data = f.read()

            dataDetailCourse = json.loads(data)

            idnumber_sikola = dataDetailCourse["idnumber_sikola"]
            shortname_sikola = dataDetailCourse["shortname_sikola"]
            kode_matkul = dataDetailCourse["kode_matkul"]
            mahasiswas = dataDetailCourse["mahasiswas"]
            dosens = dataDetailCourse["dosens"]
            sizeUserInCourse = len(dataDetailCourse["mahasiswas"]) + len(
                dataDetailCourse["dosens"]
            )

            print(f"Progress: {((currentFile / loopingSize) * 100):.2f} %")

            if idnumber_sikola not in backup_list:
                print(f"Shortname Course : {shortname_sikola}")
                # if shortname_sikola == 'TA232-124999':
                paramsAPIGetCourseByField = {
                    "wsfunction": "core_course_get_courses_by_field",
                    "field": "idnumber",
                    "value": idnumber_sikola,
                }

                responseGetCourseSikolaByField = await session.get(
                    baseUrl, params=paramsAPIGetCourseByField, ssl=False
                )

                dataCourseSikola = await responseGetCourseSikolaByField.json()
                
                task = await rps_synkron(
                    session, baseUrl, urlRps, dataCourseSikola, sizeUserInCourse, kode_matkul
                )
               
                respnsesTask = await asyncio.gather(*task)

                for res in respnsesTask:
                    resultFetch.append(await res.json())

                backup_list.append(idnumber_sikola)
                save_backup_list(backup_list)


# get fetch_sikola_course()
if __name__ == "__main__":
    asyncio.run(fetch_sikola_course_users())
