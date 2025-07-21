import aiohttp
import asyncio
import glob
import os
import pandas as pd
import requests
import json
import pickle
import csv
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

load_dotenv()

# Disable InsecureRequestWarning
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

currentDate = "2024-07-03-kendala-MKUNON"
id_prodi_sikola = "21"



def save_backup_list(
    backup_list, filename=f"log/{currentDate}_attendance_mhs_raw.pkl"
):
    with open(filename, "wb") as file:
        pickle.dump(backup_list, file)

def load_backup_list(filename=f"log/{currentDate}_attendance_mhs_raw.pkl"):
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



async def attendance_item_raw(session, baseUrl, courseData, fullname_sikola, idKelasKuliah, classDateConverted):
    print(f"Get Data {fullname_sikola}...")
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
        mahasiswaGroupId = 0
        for groups in dataCourseGroup:
            if groups["name"] == "MAHASISWA":
                mahasiswaGroupId = groups["id"]
                break

        if not mahasiswaGroupId == 0:
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
                        if module["name"] == "Presensi Mahasiswa":
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
                              

                                if (
                                    convertDate == classDateConverted
                                    and item["groupid"] == mahasiswaGroupId
                                ):
                                    resultAttendanceRaw.append(item)

                            if len(resultAttendanceRaw) > 0:
                                
                                os.makedirs(f"data/attendanceRaw/{classDateConverted}/mahasiswa/", exist_ok=True)

                                with open(
                                    f"data/attendanceRaw/{classDateConverted}/mahasiswa/{idKelasKuliah}.json",
                                    "w",
                                ) as f:
                                    json.dump(resultAttendanceRaw, f, indent=4)
                                    
                                # file_mahasiswa = f"data/revisiAttendanceRaw/{currentDate}/mahasiswa/{idKelasKuliah}-{classDateConverted}.json"
                                # file_dosen = f"data/revisiAttendanceRaw/{currentDate}/dosen/{idKelasKuliah}-{classDateConverted}.json"
                                                         
                                

                                os.makedirs(f"data/revisiAttendanceRaw/{currentDate}/mahasiswa/", exist_ok=True)
                                with open(
                                    f"data/revisiAttendanceRaw/{currentDate}/mahasiswa/{idKelasKuliah}-{classDateConverted}.json",
                                    "w",
                                ) as f:
                                    json.dump(resultAttendanceRaw, f, indent=4)
                                
                                

                            break

                            
                    break

        
    print(f"{fullname_sikola} DONE !!!")
    
    var_backup = f"{idKelasKuliah}-{classDateConverted}"
    backup_list.append(var_backup)
    save_backup_list(backup_list)

async def attendance_get_raw(session, item):
    start_date = "2024-02-19"
    end_date = "2024-07-31"
    tasks = []
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    
    try:
        for date_obj in range((end_date_obj - start_date_obj).days + 1):
            current_date = (start_date_obj + timedelta(days=date_obj)).strftime("%Y-%m-%d")
            var_load = f"{item[2]}-{current_date}"
            
            if var_load not in backup_list:

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
    except Exception as e:
        print(f"{item[2]}-{item[1]} : {e}")
async def fetch_sikola_course(fileProdi):
    async with aiohttp.ClientSession() as session:
        tasks = []
        print(f"Processing Course")
        
        df = pd.read_excel(f"{fileProdi}")
        for index, row in df.iterrows():
            try:
                tasks.append(attendance_get_raw(session, row.tolist()))
            except Exception as e:
                        print(f"{row} : {e}")
        await asyncio.gather(*tasks)
        
    
  

    

if __name__ == "__main__":
 
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"

      
    fileProdi = f"data/MK/{id_prodi_sikola}.xlsx"
    
    asyncio.run(fetch_sikola_course(fileProdi))