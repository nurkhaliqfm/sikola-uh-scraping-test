import asyncio
import csv
import os
from dotenv import load_dotenv
import aiohttp
import datetime
import json


load_dotenv()

NEOSIA_OAUTH_ACCESS_URL = os.getenv("NEOSIA_OAUTH_ACCESS_URL")
NEOSIA_OAUTH_CLIENT_ID = os.getenv("NEOSIA_OAUTH_CLIENT_ID")
NEOSIA_OAUTH_CLIENT_SECRET = os.getenv("NEOSIA_OAUTH_CLIENT_SECRET")
NEOSIA_ADMIN_MKPK_USERNAME = os.getenv("NEOSIA_ADMIN_MKPK_USERNAME")
NEOSIA_ADMIN_MKPK_PASSWORD = os.getenv("NEOSIA_ADMIN_MKPK_PASSWORD")
API_NEOSIA = os.getenv("API_NEOSIA")
TOKEN = os.getenv("TOKEN")


async def authenticate(username, password):
    # Implement your authentication logic here
    return (
        username == NEOSIA_ADMIN_MKPK_USERNAME
        and password == NEOSIA_ADMIN_MKPK_PASSWORD
    )



async def get_data(id_kelas, headers, result_data):
    try:
        print(id_kelas)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_NEOSIA}/admin_mkpk/dosen/input_nilai/kelas_kuliah/{id_kelas}",
                headers=headers,
                ssl=False,
            ) as response:
                response_data = await response.json()
            async with session.get(
                f"{API_NEOSIA}/admin_mkpk/prodi", headers=headers, ssl=False
            ) as response_fakultas:
                response_fakultas_data = await response_fakultas.json()

            id_prodi = response_data["kelasKuliah"]["prodi_semester"]["prodi"]["id"]
            nama_kelas = response_data["kelasKuliah"]["nama"]
            prodi = response_data["kelasKuliah"]["prodi_semester"]["prodi"][
                "nama_resmi"
            ]
            nama_fakultas = next(
                (
                    p["fakultas"]["nama_resmi"]
                    for p in response_fakultas_data["prodis"]
                    if p["id"] == id_prodi
                ),
                None,
            )

            result_data.append(
                [
            
                    id_kelas,
                    nama_kelas,
                    prodi,
                    nama_fakultas,
                ]
            )
    except Exception as e:
        print(
            f"Error fetching data for id_kelas = {id_kelas}: {e}"
        )
        


async def get_attendance():

    
    headers = {
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjRiZWNhMGEyYzk4Y2M5MmNjMThhMWM0MGJiMmNiZDE5OGZjZDY2NjA0MWQ2MDU4NGY4NGUzYzE4ODcwNmEwY2Q3MTAyYTk0NjU0YzRkMmI2In0.eyJhdWQiOiIyIiwianRpIjoiNGJlY2EwYTJjOThjYzkyY2MxOGExYzQwYmIyY2JkMTk4ZmNkNjY2MDQxZDYwNTg0Zjg0ZTNjMTg4NzA2YTBjZDcxMDJhOTQ2NTRjNGQyYjYiLCJpYXQiOjE3MjEzNjczMTMsIm5iZiI6MTcyMTM2NzMxMywiZXhwIjoxNzIxNzk5MzEzLCJzdWIiOiI4NTQ5NiIsInNjb3BlcyI6WyIqIl19.IG0iS6z2UOE7VtfgYdruEf4eKHm5_hVJkZO_Ml_F29KTATefVyzRi2-V-C86RL1fyiF8_EEE-iU4sTiT-IYHrt_SOcrCY2inPo-3Ks4wCHzGaW-2sUvwn9lpl0uZMYJM9vBZZK-nU-F1ZvJAzVPxufccc2Madav9TreaRuTQEcSugx3F9fb884LRAi1szE--VAw17Bnjn0BAb3eWwMIKgPzAonM3MiwqMZAl8WkthIBnNc4XD5mlDt8E9jwaPQKI9WAjVwUBZ6ICGo19l2a4tbVVuL1q8iuHOf0RQwq5tErxHw_iAqPmAsNmU9vX27tYIHaEwE_Q5iQXELQD_SB2JA3ZjdIBrypJIFWthbjCpY0558uMpTN427CeAjrl2AbRVHdy-4WuMhE8HY6QH13NbesclCfHCd3cOGCm96Efja7LvFDLK53-3m41QHk0dtuGiA38BYypNEHV3UkAOhr3Xl251E-ZtqRu-1JA2N1pxyEErUfkGv0_lKJPk90lHFGb0mNzFzSHBm4g7ubW8feAoWonOH1qHdYSte--JtyMe91AKXV5TcP8Gwg0MPkyS0Rj__B_wq-tkNfs_MDPZ-rydqwRD4Etv-k9SsTYJnbXJ-Aw1iwnEtQHwyCIGjgsFt2Mf7FHWWi8Iiuk9vQTVKXLYD6Gafxfukkm8HK_chE9lu8',
        'Cookie': 'XSRF-TOKEN=eyJpdiI6ImdFMU5SSngwYlFTOEpiY3JDTXV5K0E9PSIsInZhbHVlIjoieDVWSHpmY2lkbjZmakpTWmljSFJmWFp4MGd4YjdGOFh5WGlGSWJkclJnN3piSFwvWldHUTdEb0ZMTTYwblpmRW5sVVdjMkRyVEI5S01hMmRvYjlvbkpVcXltRWdIVWpuUWVwWUFQMWRtK1FxcWxleFwvckRTUDBPd0k3TDBQRW92ViIsIm1hYyI6IjI5YmNhZjFlMzQ3MjU2ZGRkMGVkNzY4YzViZTRlMWZhNjI0M2RjYWFmMTdiOWI0MmZhNGI1ZGUyZmMwMzcyZjcifQ%3D%3D; api_neosia_unhas_session=eyJpdiI6IjMyWGprT2NNWmNpWHRiWkFISWVtRkE9PSIsInZhbHVlIjoiSThTNjU0Mm5zckJ1c3REaHpvNWpDZWNsK3ZkUnE2K1lzTXpCSW1nQlMzNG5RVWhLYTd5eDhrUHJGcVlpZnpnbWtydzd3MjRjaFwvRHpJRm5hczY2R1RPMDl1RERWR2FOWTkzenRDbjZYMGdZNW9KUWRKZHBBQjExNCtrNzlsZlI0IiwibWFjIjoiOWY5MzFjMDEwOGE4YjFhOGUxY2ZkOGI4NmJjNjYwMTJkNGMwODhjMjAzYzE0N2YxYzY4OGExNmExMGM2ZjA2YyJ9'
    }


    result_data = []
    not_in_dosen_data = []

    tasks = []
    
    dataNilai = f"data/DataExternal/NilaiDBSinkron.json"
    with open(dataNilai, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract unique kelasId values
    unique_kelas_ids = {item["kelasId"] for item in data}
    
    print(len(unique_kelas_ids))
    tasks = []
    for id_kelas in unique_kelas_ids:
        tasks.append(get_data(id_kelas, headers, result_data))
       
        

    await asyncio.gather(*tasks)

    with open(
        f"data/CourseReport2/NilaiDB.csv", "w", newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                # "tanggal_rencana",
                "id_kelas",
                "nama_kelas",
                "prodi",
                "nama_fakultas",
                # "keterangan",
            ]
        )
        writer.writerows(result_data)




if __name__ == "__main__":
    asyncio.run(get_attendance())
