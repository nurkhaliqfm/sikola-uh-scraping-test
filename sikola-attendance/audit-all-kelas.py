import aiohttp
import asyncio
import glob
import os
import requests
import json
import pandas as pd

import pickle
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

async def audit(todays):
      #CEK NOT IN MAHASISWA AND NOT IN DOSEN REVISI ABSENSI
    dosen_folder = f"data/revisiAbsensi/{todays}/dosen"
    mahasiswa_folder = f"data/revisiAbsensi/{todays}/mahasiswa"

    dosen_files = os.listdir(dosen_folder)
    mahasiswa_files = os.listdir(mahasiswa_folder)
    
    dosen_id_kelas = [filename.split(".")[0] for filename in dosen_files]
    mahasiswa_id_kelas = [filename.split(".")[0] for filename in mahasiswa_files]

    not_in_mahasiswa = [filename for filename in dosen_id_kelas if filename not in mahasiswa_id_kelas]
    not_in_dosen = [filename for filename in mahasiswa_id_kelas if filename not in dosen_id_kelas]

    json_not_in_mahasiswa = []

    for id_kelas in not_in_mahasiswa + not_in_dosen:
        folder = dosen_folder if id_kelas in not_in_mahasiswa else mahasiswa_folder
        keterangan = "TANGAL PRESENSI TIDAK ADA DI MAHASISWA" if id_kelas in not_in_mahasiswa else "TANGGAL PRESENSI TIDAK ADA DI DOSEN"

        with open(f"{folder}/{id_kelas}.json") as file:
            data = json.load(file)

            for item in data:
                json_not_in_mahasiswa.append([item['nama_matakuliah'], item['pertemuan']['id_kelas_kuliah'], item['pertemuan']['tanggal_rencana'], keterangan])

   
 
 
async def audit_all():
    
    async with aiohttp.ClientSession() as session:
        task = []
        all_kelas = []

        for filePath in listDataDetailKelasFile:
            with open(filePath, "r",  encoding="utf-8") as f:
                data = f.read()

            dataDetailCourse = json.loads(data)

            nama_prodi = dataDetailCourse["nama_prodi"]
            id_prodi = dataDetailCourse["id_prodi"]
            nama_kelas = dataDetailCourse["nama_kelas"]
            nama_matkul = dataDetailCourse["nama_matkul"]
            id_kelas = dataDetailCourse["shortname_sikola"].split("-")[1]
            
            with open(list_fakultas, "r",  encoding="utf-8") as file_f:
                data = file_f.read()
                dataJson = json.loads(data)
                nama_fakultas = next((p['fakultas']['nama_resmi'] for p in dataJson['prodis'] if p['id'] == id_prodi), None)
                print(nama_fakultas)
                all_kelas.append([nama_kelas, id_kelas, nama_prodi, nama_fakultas])
  
    # start_date = "2024-02-19"
    # end_date = "2024-03-31"
    
    # start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    # end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    # lecturer_folder = "data/attendanceRaw"
    # result_folder = "data/cekPresensi/null"

    # os.makedirs(result_folder, exist_ok=True)

    # json_not_in_mahasiswa = []
    # nullDosen = []

    # tasks = []
    # for date_obj in range((end_date_obj - start_date_obj).days + 1):
    #     current_date = (start_date_obj + datetime.timedelta(days=date_obj)).strftime("%Y-%m-%d")
    #     tasks.append(audit(current_date))
    
    
    with pd.ExcelWriter(f"data/MK/Hasil Audit ALL Kelas.xlsx") as writer:
        df = pd.DataFrame(all_kelas, columns=["fullname_kelas_sikola", "id_kelas_kuliah", "nama_prodi", "nama_fakultas"])
        df.to_excel(writer, index=False)
    
  
if __name__ == "__main__":
    kelasActiveName = "TA232.12"
    listDataDetailKelasFile = glob.glob(f"data/detailkelas/{kelasActiveName}/*.json")
    list_fakultas = "data/DataExternal/prodi.json"


   
    asyncio.run(audit_all())
    
    
     
