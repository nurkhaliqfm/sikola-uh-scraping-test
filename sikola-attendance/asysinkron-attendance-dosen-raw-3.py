import aiohttp
import asyncio
import glob
import os
import pandas as pd
import requests
import json
import pickle
import csv
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

# Disable InsecureRequestWarning
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



async def attendance_item_raw(session, baseUrl, courseData, fullname_kelas, idKelasKuliah, classDateConverted):
    print(f"Get Data {fullname_kelas}...")
    resultAttendanceRaw = []
    paramsAPIGetCourseGroup = {
        "wsfunction": "core_group_get_course_groups",
        "courseid": courseData,
    }

    responseGETCourseGroup = await session.get(
        baseUrl, params=paramsAPIGetCourseGroup, ssl=False
    )

    dataCourseGroup = await responseGETCourseGroup.json()
    if not len(dataCourseGroup) == 0:
        dosenGroupId = 0
        for groups in dataCourseGroup:
            if groups["name"] == "DOSEN":
                dosenGroupId = groups["id"]
                break

        if not dosenGroupId == 0:
            paramsAPIGetCourseContent = {
                "wsfunction": "core_course_get_contents",
                "courseid": courseData,
            }

            responseGetCourseContent = await session.get(
                baseUrl, params=paramsAPIGetCourseContent, ssl=False
            )

            dataCourseContent = await responseGetCourseContent.json()
            for content in dataCourseContent:
                if content["name"] == "Info Matakuliah":
                    for module in content["modules"]:
                        if module["name"] == "Presensi Pengampu Mata Kuliah":
                            attendanceId = module["instance"]

                            paramsAttendaceSession = {
                                "wsfunction": "mod_attendance_get_sessions",
                                "attendanceid": attendanceId,
                            }

                            responseAttendanceSessions = await session.get(
                                baseUrl, params=paramsAttendaceSession, ssl=False
                            )

                            dataSessionsAttendance = (
                                await responseAttendanceSessions.json()
                            )

                            for item in dataSessionsAttendance:
                                sessDate = item["sessdate"]
                                convertDate = (
                                    datetime.fromtimestamp(sessDate, timezone.utc)
                                    + timedelta(hours=8)
                                ).strftime("%Y-%m-%d")
                              
                                
                                # classDateConverted = classDate.strftime("%Y-%m-%d")
                               

                                if (
                                    convertDate == classDateConverted
                                    and item["groupid"] == dosenGroupId
                                ):
                                    resultAttendanceRaw.append(item)

                            if len(resultAttendanceRaw) > 0:
                                os.makedirs(f"data/attendanceRaw/{classDateConverted}/dosen/", exist_ok=True)

                                with open(
                                    f"data/attendanceRaw/{classDateConverted}/dosen/{idKelasKuliah}.json",
                                    "w",
                                ) as f:
                                    json.dump(resultAttendanceRaw, f, indent=4)
                                os.makedirs(f"data/revisiAttendanceRaw/{currentDate}/dosen/", exist_ok=True)
                                with open(
                                    f"data/revisiAttendanceRaw/{currentDate}/dosen/{idKelasKuliah}-{classDateConverted}.json",
                                    "w",
                                ) as f:
                                    json.dump(resultAttendanceRaw, f, indent=4)

                            break
                    break
                
    print(f"{fullname_kelas} DONE..!!")
    # backup_list.append(courseData["courses"][0]["shortname"])
    # save_backup_list(backup_list)


#


async def attendance_get_raw(session, item):
    # id_kelas = item[1]
    # fullname = item[0]
    
    start_date = "2024-02-19"
    end_date = "2024-04-29"
    tasks = []
    
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

    for date_obj in range((end_date_obj - start_date_obj).days + 1):
        current_date = (start_date_obj + timedelta(days=date_obj)).strftime("%Y-%m-%d")
        shortname_sikola = f"TA232-{item[2]}"
        print(shortname_sikola)
        paramsAPIGetCourseByField = {
            "wsfunction": "core_course_get_courses_by_field",
            "field": "shortname",
            "value": shortname_sikola,
        }

      
        print(current_date)
        tasks.append(attendance_item_raw(session, baseUrl, item[0], item[1], item[2], current_date))
        
        
    await asyncio.gather(*tasks)

    
async def delete_parsing():
    # id_kelas = item[1]
    # fullname = item[0]
    tasks = []
    print(f"Processing Course")
    
    df = pd.read_excel(f"{fileProdi}")
    start_date = "2024-02-19"
    end_date = "2024-04-29"
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    for index, row in df.iterrows():
        for date_obj in range((end_date_obj - start_date_obj).days + 1):
            current_date = (start_date_obj + timedelta(days=date_obj)).strftime("%Y-%m-%d")
            file_path = f"data/absensi/{current_date}/dosen/{row[2]}.json"
            file_path_mahasiswa = f"data/absensi/{current_date}/mahasiswa/{row[2]}.json"

            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            if os.path.exists(file_path_mahasiswa):
                os.remove(file_path_mahasiswa)
                print(f"Deleted file: {file_path_mahasiswa}")
            
                
                

    
   
      
async def fetch_sikola_course(fileProdi):
    async with aiohttp.ClientSession() as session:
        tasks = []
        print(f"Processing Course")
        
        df = pd.read_excel(f"{fileProdi}")
        for index, row in df.iterrows():
            tasks.append(attendance_get_raw(session, row.tolist()))
    

        await asyncio.gather(*tasks)
   
       

async def get_course_byid():
    result_data = []
   
    async with aiohttp.ClientSession() as session:
        params = {
            "wsfunction": "core_course_get_courses_by_field",
            "field": "category",
            "value": id_prodi_sikola,
        }
        
        responseGetCourse = await session.get(
            baseUrl, params=params, ssl=False
        )
        
        data = await responseGetCourse.json()
        print(len(data['courses']))
        
        for course in data['courses']:
            if "TA232" in course['shortname']:
                id_kelas = course['shortname'].split('-')[1]
                fullname = course['fullname']
                id_course_sikola = course['id']
                print(id_kelas)
                
                result_data.append([id_course_sikola, fullname, id_kelas])
    
    os.makedirs(f"data/MK/", exist_ok=True)

    with pd.ExcelWriter(f"data/MK/{id_prodi_sikola}.xlsx") as writer:
        df = pd.DataFrame(result_data, columns=["id_course_sikola","fullname", "id_kelas"])
        df.to_excel(writer, index=False)
        
    
if __name__ == "__main__":
  
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"
    
    
    currentDate = "2024-04-26-kendala-INFORS1"
    id_prodi_sikola = "185"
    fileProdi = f"data/MK/{id_prodi_sikola}.xlsx"

    # asyncio.run(get_course_byid())
    # asyncio.run(fetch_sikola_course(fileProdi))
    asyncio.run(delete_parsing())