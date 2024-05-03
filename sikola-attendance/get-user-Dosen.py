import requests
import os
import json
import asyncio
import aiohttp
import csv
from dotenv import load_dotenv
import pandas as pd

load_dotenv()


API_NEOSIA = os.getenv('API_NEOSIA')

async def fetch_data(user_id, session):
    try:
      
        urlFetch = f"https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json&wsfunction=core_user_get_users_by_field&field=id&values[0]={user_id}"
        async with session.get(urlFetch, ssl=False) as response:
            if response.headers['Content-Type'] == 'application/json':
                dataDosen = await response.json()
                return dataDosen
            else:
                print(f"Unexpected content type received for user {user_id}")
                return None
    except aiohttp.ClientConnectorError as e:
        print(f"Error fetching data for user {user_id}: {e}")
        return None
async def process_data(user, session):
    user_id = user['id']
    try:
        
        dataDosen = await fetch_data(user_id, session)
        with open(f"data/ListDosen/{user_id}.json", "w") as f:
                json.dump(dataDosen, f, indent=4)
        # if dataDosen[0]['username'].startswith('1'):
        #     print("Non-praktisi-1", user_id)
        #     os.makedirs(f"data/Dosen-1/", exist_ok=True)
            
        # if dataDosen[0]['username'].startswith('7'):
        #     print("Non-praktisi-7", user_id)
        #     os.makedirs(f"data/Dosen-7/", exist_ok=True)
        #     with open(f"data/Dosen-7/{user_id}.json", "w") as f:
        #         json.dump(dataDosen, f, indent=4)
        # if not dataDosen[0]['username'].isdigit():
        #     print("praktisi", user_id)
        #     os.makedirs(f"data/DosenPraktisi/", exist_ok=True)
        #     with open(f"data/DosenPraktisi/{user_id}.json", "w") as f:
        #         json.dump(dataDosen, f, indent=4)
        
    except Exception as e:
        print(f"An error occurred during processing data for user {user_id}: {e}")
async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for foldername in os.listdir(folder_path):
            if start_date <= foldername <= end_date:
                folder_full_path = os.path.join(folder_path, foldername, "dosen")
                for filename in os.listdir(folder_full_path):
                    if filename.endswith(".json"):
                        with open(os.path.join(folder_full_path, filename), 'r') as file:
                            data = json.load(file)
                            for user in data[0]['users']:
                                tasks.append(process_data(user, session))
        await asyncio.gather(*tasks)



async def getDosenPraktisi(filename, folder_praktisi, headers, result_data, session):
    if filename.endswith(".json"):
        with open(os.path.join(folder_praktisi, filename), 'r') as file:
            data = json.load(file)
            if 'idnumber' in data[0]:
                idnumber= data[0]['idnumber']
                fullname= data[0]['fullname']
                print(idnumber)
                user_id = filename.split(".json")[0]
                urldataDosen = f"https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json&wsfunction=core_enrol_get_users_courses&userid={user_id}"
                try:
                    async with session.get(urldataDosen, ssl=False) as response:
                        dataDosen = await response.json()
                        for course in dataDosen:
                            id_kelas = course['shortname'].split('-')[1]
                            courseid = course['id']
                            
                            paramsAPIGetCourseContent = {
                                "wsfunction": "core_course_get_contents",
                                "courseid": courseid,
                            }

                            responseGetCourseContent = await session.get(
                                baseUrl, params=paramsAPIGetCourseContent, ssl=False
                            )

                            dataCourseContent = await responseGetCourseContent.json()
                            
                            print(course['fullname'], idnumber, id_kelas)
                            async with session.get(
                                f"{API_NEOSIA}/admin_mkpk/dosen/input_nilai/kelas_kuliah/{id_kelas}",
                                headers=headers,
                                ssl=False
                            ) as response:
                                response_data = await response.json()
                            
                            async with session.get(
                                f"{API_NEOSIA}/admin_mkpk/prodi",
                                headers=headers,
                                ssl=False
                            ) as response_fakultas:
                                response_fakultas_data = await response_fakultas.json()

                            id_prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['id']
                            nama_kelas = response_data['kelasKuliah']['nama']
                            prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['nama_resmi']
                            nama_fakultas = next((p['fakultas']['nama_resmi'] for p in response_fakultas_data['prodis'] if p['id'] == id_prodi), None)
                            
                            # data = {
                            #     "nama_matakuliah": dataCourseSikola["courses"][0]["fullname"],
                            #     "pertemuan": {
                            #         "tanggal_rencana": tanggalRencana,
                            #         "id_kelas_kuliah": idKelasKuliah,
                            #         "pertemuan_ke": pertemuanKe,
                            #         "tema": "",
                            #         "pokok_bahasan": "",
                            #         "keterangan": "",
                            #     },
                            #     "presensi": presensiDosens,
                            # }
                            result_data.append([idnumber, fullname, nama_kelas, prodi, nama_fakultas])
                                                            
                        
                            
                        else:
                            print(f"Unexpected content type received for user {user_id}")
                            return None
            
                except aiohttp.ClientConnectorError as e:
                    print(f"Error fetching data for user {user_id}: {e}")
                    return None
    
    
async def getListMk(filename, folder_praktisi, headers, result_data, session):
    if filename.endswith(".json"):
        with open(os.path.join(folder_praktisi, filename), 'r') as file:
            data = json.load(file)
            if 'idnumber' in data[0]:
                idnumber= data[0]['idnumber']
                username= data[0]['username']
                fullname= data[0]['fullname']
                user_id = filename.split(".json")[0]
                # urldataDosen = f"https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json&wsfunction=core_enrol_get_users_courses&userid={user_id}"
                paramsCourses = {
                    "wsfunction": "core_enrol_get_users_courses",
                    "userid": user_id,
                }
                response = await session.get(baseUrl, params=paramsCourses, ssl=False)
                
                dataDosen = await response.json()
                listData = []
                listDosen = []
                for index, course in enumerate(dataDosen):
                    # print(index+1)
                    if "TA232" in course['shortname']: 
                        id_kelas = course['shortname'].split('-')[1]
                        courseid = course['id']
                    
                        paramsAPIGetCourseContent = {
                            "wsfunction": "core_course_get_contents",
                            "courseid": courseid,
                        }

                        responseGetCourseContent = await session.get(
                            baseUrl, params=paramsAPIGetCourseContent, ssl=False
                        )

                        dataCourseContent = await responseGetCourseContent.json()
                        arrayContent = []

                        for content in dataCourseContent:
                            if content['name'] != 'Info Matakuliah':
                                dataContent = {
                                    "nama_content" : content['name'],
                                    "jumlah_content": len(content['modules'])
                                }
                                arrayContent.append(dataContent)
                    
                                
                                


                                # break
                                # print(content['name'], )
                        listMk = {
                            "username": username,
                            "nama_dosen": fullname,
                            "id_kelas_kuliah":id_kelas,
                            "nama_kelas": course['fullname'],
                            "contents":arrayContent,
                                
                        }
                        listData.append(listMk)
                        
                        
                        
                        # print(listData)
                        # break
                        
                        
                        
                os.makedirs(f"data/PerkuliahanDosen/", exist_ok=True)
                with open(
                    f"data/PerkuliahanDosen/{username}.json",
                    "w",
                ) as f:
                    json.dump(listData, f, indent=4)
                    # async with session.get(
                    #     f"{API_NEOSIA}/admin_mkpk/dosen/input_nilai/kelas_kuliah/{id_kelas}",
                    #     headers=headers,
                    #     ssl=False
                    # ) as response:
                    #     response_data = await response.json()
                    
                    # async with session.get(
                    #     f"{API_NEOSIA}/admin_mkpk/prodi",
                    #     headers=headers,
                    #     ssl=False
                    # ) as response_fakultas:
                    #     response_fakultas_data = await response_fakultas.json()

                    # id_prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['id']
                    # nama_kelas = response_data['kelasKuliah']['nama']
                    # prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['nama_resmi']
                    # nama_fakultas = next((p['fakultas']['nama_resmi'] for p in response_fakultas_data['prodis'] if p['id'] == id_prodi), None)

                    # result_data.append([idnumber, fullname, nama_kelas, prodi, nama_fakultas])
                                                    

        
    
async def fetchListDosenCourse():
    async with aiohttp.ClientSession() as session:

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjE5OGIwZjY2NmVkNjEwYTc3MTZmZmJiM2NlOTgzMTA3YTQ1YTE1MjQ0OWUwY2RiNTU0MjQ0ZDRiYTA1YmExZTExZWQ4NmVkODQ4YTU3NDFiIn0.eyJhdWQiOiIyIiwianRpIjoiMTk4YjBmNjY2ZWQ2MTBhNzcxNmZmYmIzY2U5ODMxMDdhNDVhMTUyNDQ5ZTBjZGI1NTQyNDRkNGJhMDViYTFlMTFlZDg2ZWQ4NDhhNTc0MWIiLCJpYXQiOjE3MTQxMDgwMjYsIm5iZiI6MTcxNDEwODAyNiwiZXhwIjoxNzE0NTQwMDI2LCJzdWIiOiI4NTQ5NiIsInNjb3BlcyI6WyIqIl19.QPjZ88RwPVRt51JTO0Uc2Oj8ph0U6t92Z5UlEv6PDgYMwytZqU_z7KT_dUj-JBp8BljFHstHayolP2lXx90PwQgv33c04VHBys0TQDdBLs8iSIblqOZiY7wayuiD4Rud1la9FbrGVC6fykF3XDR1e1MbV5xsSk-cNsIJqZ6LjfqluBOZABWBRIfYQ8NcHgOEOW-r51UPxwlSdTQqPZif10q_b981lSUu5CuCCWmRgI6YjfTmHxgTjl8zAdjTi1w7pawb10IlvPN7Xphzp_0vTNxs1HO_pROOSKZTB9908jGKIUgcV5C6bcvzmitTPLMUbfM3xyLi0-Z7Gn8wugBM4jVNNSV8ricch2umD7l8XDboszm8YA8vh5LamQuZNsZKQE873pWUrq2xGDA8Wd0WLnze-1ymmx-g0XNa89JTnj_hZuHKcv8JkWHbXDGY3sYtq6PiKYaiJQaFDKyFvt7IfpkiHr3xi6yCxrGy0ExsGw4Jf58SvubrHHg1aekQkTDZ1BZWUokpof4pwWGU2JG_EO3zfNJYtyW2oXd9xgFnSXcWnx18LsF1NYCoacreSIoFjYwrmKtzjELrKeN0yft6ShHCe8g6RJynFjzaK-ggTxnM6OsNzx0RI1tODeOE55rb9Vtl_7mmSV02Sr3UmqQrOhs-LRXXv-z_lemdDaDrVYQ',
            'Cookie': 'XSRF-TOKEN=eyJpdiI6Im1kVERueXFVNFNMOU56ZzdGR2tcL2hnPT0iLCJ2YWx1ZSI6InBxeEgwQnpWdWpsN3FiNFBXeGN3aVJWVENyVUpxSkMyMnh5aWRLZXNSMk0wM0U4RFlhV2JtZHZJcG16ZWQ3WVJHTnpxZFZcL0FEQ0tFSlZOd2pOMkpaUHZFUmg2OUZUdExlYVNrOTl6SmhCZ0NxUXdYV3U0ek14cWw1OVpPRk4xaCIsIm1hYyI6IjYxNThkM2FkODhmMTA0YTEyYjY4ZDlkZDFlNjIzYzIwYWMyMzY3N2JmYjE0OTcwNjBkYTM0YWUzNDI3MmM0YTkifQ%3D%3D; api_neosia_unhas_session=eyJpdiI6ImVvRjRwdUV2ck1YUU9LZ2JKMzU2Ymc9PSIsInZhbHVlIjoia29zRXNRXC9MM1RBakFYSHErc1ZMRHJHR0dINGJBeWZEeXI0dklUdFwvelVVXC96MVVBVTFPSmc3cEpqbTNCK3c2cTJlZTR5bngrY1NlRWdJQ2lIa1lhSE55b3lnbUk5U25mdEs2RWluWWdcL0h4OGxlNUdYT1hQMHZvb082WWM2aHh4IiwibWFjIjoiNzFhODI4ZTM4Y2U5NDE5YmNmMjgxNmJkNmQzZTZiMjQzYmI3NzYwNjM5Y2E5YmM3NTUyYmNjYzY5MWY0NjQyNCJ9'
        }

        folder_praktisi = 'data/ListDosen/'
        folder_praktisi = 'data/ListDosen/'
        folder_hasil = 'data/PerkuliahanDosen/'

        result_data = []
        arrayContent = []
        tasks = []
        
        nomor = None
        nomor_kelas = 1
        dosens = {}

        for filename in os.listdir(folder_praktisi):
            tasks.append(getListMk(filename, folder_praktisi, headers, result_data, session))
        await asyncio.gather(*tasks)
  
        
   
              
async def convert_excel():  
    folder_hasil = 'data/PerkuliahanDosen/'

    result_data = []
    
    nomor = None
    nama_dosen = None
    nomor_kelas = 1
    dosens = {}       
    for filename in os.listdir(folder_hasil):
        if filename.endswith(".json"):
            with open(os.path.join(folder_hasil, filename), 'r', encoding='utf-8') as file:
                dataList = json.load(file)
                for i, dosen in enumerate(dataList):
                    nama_dosen = dosen['nama_dosen']
                    if nama_dosen not in dosens:
                        nomor = len(dosens) + 1
                        dosens[nama_dosen] = nomor
                        nomor_kelas = 1
                    else:
                        nomor_kelas += 1
                    dataCourseContent = dosen['contents']
                    total_jumlah_content = sum([content['jumlah_content'] for content in dataCourseContent])
                    # print(total_jumlah_content)
                    # if i == 0 or dosen['nama_dosen'] != dataList[i-1]['nama_dosen']:
                    #     nomor = 1
                    #     nomor_kelas = 1
                    if nomor_kelas == 2:
                        nomor = None
                    if nomor_kelas != 1:
                        nama_dosen = None
                    result_data.append([nomor, nama_dosen, nomor_kelas, dosen['nama_kelas'], total_jumlah_content])
                  

    with pd.ExcelWriter(f"{folder_hasil}/ListKelasDosen.xlsx") as writer:
            df = pd.DataFrame(result_data, columns=["NOMOR","NAMA FASILITATOR", "ket", "PERTEMUAN MK YANG TERISI MATERI", "ket"])
            # df = df.sort_values(by='NAMA FASILITATOR', ascending=True)
            df.to_excel(writer, index=False)
       
                                
if __name__ == "__main__":
  
 
  start_date = "2024-03-04"
  end_date = "2024-03-10"
  folder_path = "data/attendanceRaw/"
  
  baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"

  
#   asyncio.run(main())
  asyncio.run(convert_excel())
#   asyncio.run(fetchListDosenCourse())
# for foldername in os.listdir(folder_path):
#     if start_date <= foldername <= end_date:
#         folder_full_path = os.path.join(folder_path, foldername, "dosen")
#         for filename in os.listdir(folder_full_path):
#           if filename.endswith(".json"):
#               with open(os.path.join(folder_full_path, filename), 'r') as file:
#                   data = json.load(file)
#                   for user in data[0]['users']:
#                       user_id = user['id']
#                       url = f"https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json&wsfunction=core_user_get_users_by_field&field=id&values[0]={user_id}"

#                       payload = {}
#                       headers = {}
#                       response = requests.request("GET", url, headers=headers, data=payload)
#                       dataDosen = response.json()
                      
#                       # print(dataDosen[0]['username'])
                      
#                       if dataDosen[0]['username'].isdigit():
#                           os.makedirs(f"data/Dosen/", exist_ok=True)
#                           with open(f"data/Dosen/{user_id}.json", "w") as f:
#                               json.dump(dataDosen, f, indent=4)
#                       else:
#                           os.makedirs(f"data/DosenPraktisi/", exist_ok=True)
#                           with open(f"data/DosenPraktisi/{user_id}.json", "w") as f:
#                               json.dump(dataDosen, f, indent=4)
                      
                      