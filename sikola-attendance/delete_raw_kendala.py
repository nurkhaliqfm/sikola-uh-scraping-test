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


async def delete_parsing():
    # id_kelas = item[1]
    # fullname = item[0]
    tasks = []
    print(f"Processing Course")
    
    df = pd.read_excel(f"data/DataExternal/{fileDataForm}")
    unique_ids = df.drop_duplicates(subset=['id_kelas_kuliah'])[['fullname_kelas_sikola', 'id_kelas_kuliah']]

    start_date = "2024-02-19"
    end_date = "2024-05-13"
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    for index, row in unique_ids.iterrows():
        for date_obj in range((end_date_obj - start_date_obj).days + 1):
            current_date = (start_date_obj + timedelta(days=date_obj)).strftime("%Y-%m-%d")
            file_path = f"data/absensi/{current_date}/dosen/{row[1]}.json"
            file_path_mahasiswa = f"data/absensi/{current_date}/mahasiswa/{row[1]}.json"

            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            if os.path.exists(file_path_mahasiswa):
                os.remove(file_path_mahasiswa)
                print(f"Deleted file: {file_path_mahasiswa}")
if __name__ == "__main__":
    kelasActiveName = "TA232.12"
    fileDataForm = "kendala.xlsx"
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"
    
    
    # id_prodi_sikola = 68
    # fileProdi = f"data/MK/{id_prodi_sikola}.xlsx"

    asyncio.run(delete_parsing())