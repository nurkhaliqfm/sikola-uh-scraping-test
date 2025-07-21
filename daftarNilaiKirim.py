import aiohttp
import asyncio
import os
import json
import pickle
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Disable InsecureRequestWarning
from urllib3.exceptions import InsecureRequestWarning
import requests
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Load progress from backup
def load_backup(file_name):
    if os.path.exists(file_name):
        with open(file_name, "rb") as f:
            return pickle.load(f)
    return {"processed_prodi": set(), "data_reports": []}

# Save progress to backup
def save_backup(file_name, data):
    with open(file_name, "wb") as f:
        pickle.dump(data, f)

async def process_grade_items(session, course, data_reports, headersLogin, url_kirim):
    """
    Process grade items for a specific course and append the results to the report.
    """
    kelas_id = int(course["ID Kelas"])
    keterangan = course["Keterangan"]    

    url = f"https://sikola-v2.unhas.ac.id/grade/nilai-sikola.php?kelas_id={kelas_id}"
    headers = {
        "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTczMTkwMjgxMywianRpIjoiNmNmM2U3NzItMTZmNi00MTc3LTljNDktM2U1Y2ZmYjYwZDQwIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiJleGFtcGxlX3VzZXIiLCJuYmYiOjE3MzE5MDI4MTMsImNzcmYiOiJkNzdlZDg2NC1mMTY5LTQ1YjAtOGI2Zi05MWM4ZTYwNTJjNWUiLCJleHAiOjE3MzQ0OTQ4MTN9.CQxdPCmAPE6rAGJvVqs9Jxfu3XFHty-mbNox4b_FDbA"  # Load token securely
    }
    data_parsing = []
    payload = []
    
    try:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            if data and isinstance(data, list) and keterangan == "Ada Nilai di Sikola (Belum Konfirmasi)":
                
                for usergrade in data:
                    data_parsing.append({
                        'courseid': usergrade['courseid'],
                        'courseidnumber': usergrade['courseidnumber'],
                        'id_matkul': usergrade['id_matkul'],
                        'id_kelas_kuliah': usergrade['id_kelas_kuliah'],
                        'id_prodi': usergrade['id_prodi'],
                        'userid': usergrade['userid'],
                        'userfullname': usergrade['userfullname'],
                        'useridnumber': usergrade['useridnumber'],
                        'maxdepth': usergrade['maxdepth'],
                        'nilai_khusus': usergrade['nilai_khusus'],
                        'gradeitems': usergrade['gradeitems'],
                    })
                
                
                payload = {
                    'username' : 'adminneosikola',
                    'kelas_id' : int(kelas_id),
                    'data_nilai' : json.dumps(data_parsing)
                }
                with open(
                    f"data/nilai/{kelas_id}.json",
                    "w",
                ) as f:
                    json.dump(payload, f, indent=4)

                
                payload = json.dumps(payload)
                
                kirimNilai = await session.post(url_kirim+"/kirim_nilai", data=payload, headers=headersLogin, ssl=False)
                response = await kirimNilai.json()
                
                response = response['detail']
                print(response)
                
                
    except Exception as e:
        print(f"Error processing course {kelas_id}: {e}")
        
        

async def fetch_course_data():
    async with aiohttp.ClientSession() as session:
        backup_file = "kirim_nilai_sipakamase.pkl"
        active_semester = "TA242"

        # Load progress from backup
        backup_data = load_backup(backup_file)
        processed_prodi = backup_data.get("processed_prodi", set())
        data_reports = backup_data.get("data_reports", [])

        # Load course names from Excel
        excel_file = "data/lists_2.xlsx"
        df_courses = pd.read_excel(excel_file)

        # Ensure consistent column names
        df_courses.columns = df_courses.columns.str.strip()
        
        url_kirim = "http://sipakamase.unhas.ac.id:8104"

        payload = 'username=sikola&password=Tr4%2345%23kgdr%40%5Ddfgd%7Bd12'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': '*/*'
        }
        loginRps = await session.post(url_kirim+"/token", data=payload, headers=headers, ssl=False)
        getToken = await loginRps.json()
                
        tokenRps = getToken['access_token']

        headersLogin = {
            'Content-Type': 'application/json',
            "Authorization": f"Bearer {tokenRps}"
        }
        # print(headersLogin)
        
        for _, row in df_courses.iterrows():
            course = row.to_dict()
            
            await process_grade_items(session, course, data_reports, headersLogin, url_kirim)

        # Generate Excel report
  

        # Remove backup after success
        if os.path.exists(backup_file):
            os.remove(backup_file)

if __name__ == "__main__":

    asyncio.run(fetch_course_data())
