import os
import json
import pickle
import pandas as pd
import aiohttp
import asyncio

def load_backup(file_name):
    if os.path.exists(file_name):
        with open(file_name, "rb") as f:
            return pickle.load(f)
    return None

def save_backup(file_name, data):
    with open(file_name, "wb") as f:
        pickle.dump(data, f)

async def process_course(session, baseUrl, course, fakultas_sheets, fakultas, nama_prodi, backup_file):
    courseid = course["id"]
    
    if '.' not in course['idnumber']:
        print(f"Skipping course with idnumber: {course['idnumber']}")
        return
    kelas_id = course['idnumber'].split('.')[1]
    
    url = f"https://sikola-v2.unhas.ac.id/grade/surveyNilai.php?kelas_id={kelas_id}&courseid={courseid}"
    headers = {
        "Authorization": f"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIyIiwianRpIjoiMDRkYzg1MjNmOWZiNjUwZGUxYTQ3MzExMjdjOTEyY2M5OTQ0NWZlYjkwY2VkYjY4YjNlNjk2MjFkZjY2ZmZmMWVlMzZhZTkwMmE0ZTU3YjEiLCJpYXQiOjE3MzY0ODE0MTMuOTY0Nzg2LCJuYmYiOjE3MzY0ODE0MTMuOTY0Nzg5LCJleHAiOjE3MzY5MTM0MTMuOTI4NzczLCJzdWIiOiI4NTQ5NiIsInNjb3BlcyI6WyIqIl19.Q1oxrYC7P1tEYRjGz0V8Zas9gm6QeZDfw7S6pztDhS3IsRAa6YSskEWz7qQzZxjGCAPfjnLb2TvP-38EepiQ_BsFkUtVLAhWQninh_D_CDSCZn9Ed9For88X86ZGTxxO0vF_0I-TSVIeybQR7FpXSwJwq_ntQj2YFOicMzkYGAyblSD0v8hRL8LfMVonCoD8KqNHQ1mzT9VUrXharKThBFrkU9I3saKvZuYApVeVkH0Piks_XFKcG9IeKm122bcUToqwmqH7zH4a3nSHny-t8XybfYkT8Fm4lELloh-2zjKCZN6TNEZY17NrV4lbcPnz7r_gyxAXgxqhiwmnjoSBZ9jQI_Gx44Pn2gC5egeCnbTfsRl_tLAzf-Kf5K6rVQ2AS0ADebq8b84RfsmJNt6pTZ7oTeKORL-ls71C0thREHWFr79xIGsNlw9na7SVHpuF06VAWpMDMt-VUrur0HEYQqBu-_heKMRdW7xqxKxge7aH0d87Hl4FC5D9CGenwxHf6Lk2akdpjCev5834K3wHg9m1RKQ3Y6TPfyLBtGWlxjCAGDdivbkHCztWhKlbqfXVH35q5CoFQ37CfHiXmqGMlT01o0ABzs955Ls28kclFZGkC2jOPiGWvqVcNHVSmULlwe35Gn-vH7ee1LKqRhxPbkb5idHOtmPWbiUKuFQ3bjw"  # Load token securely
    }

    try:
        async with session.get(url, headers=headers) as response:
            dataSurvey = await response.json()
            if not dataSurvey:
                return

            for entry in dataSurvey:
                if fakultas not in fakultas_sheets:
                    fakultas_sheets[fakultas] = []

                fakultas_sheets[fakultas].append({
                    "Fakultas": fakultas,
                    "Prodi": nama_prodi,
                    "Mata Kuliah": entry.get("nama_mk"),
                    "Kode MK": entry.get("kode_mk"),
                    "ID Kelas": entry.get("kelas_kuliah_id"),
                    "Nama Kelas": entry.get("nama_kelas"),
                    "Pertanyaan": entry.get("pertanyaan"),
                    "Jawaban Essai": entry.get("jawaban") if entry.get("type_pertanyaan") == "textarea" else "",
                    "Jawaban Multiple Choice": entry.get("jawaban") if entry.get("type_pertanyaan") == "radio" else "",
                    "Nama Dosen": entry.get("dosen"),
                    "NIP Dosen": entry.get("nip"),
                })

            # Save backup after processing each course
            save_backup(backup_file, {"fakultas_sheets": fakultas_sheets})

    except Exception as e:
        print(f"Error processing course {kelas_id}: {e}")

async def fetch_sikola_course():
    async with aiohttp.ClientSession() as session:
        active_semester = "TA241"
        backup_file = "backup_survey_TA241-2.pkl"
        backup_data = load_backup(backup_file)
        processed_prodi = set(backup_data["processed_prodi"]) if backup_data else set()
        fakultas_sheets = backup_data["fakultas_sheets"] if backup_data else {}

        with open("data/prodi_semester.json", "r", encoding="utf-8") as faculty_file:
            datafakultasProdi = json.load(faculty_file)

        for prodi in datafakultasProdi["prodis"]:
            nama_prodi = prodi["nama_resmi"]

            if nama_prodi in processed_prodi:
                continue

            fakultas = prodi["fakultas"]["nama_resmi"]

            param_prodi = {
                "wsfunction": "core_course_get_categories",
                "criteria[0][key]": "name",
                "criteria[0][value]": nama_prodi,
            }

            response = await session.get(baseUrl, params=param_prodi, ssl=False)
            response = await response.json()

            if not response:
                continue

            param_prodi_courses = {
                "wsfunction": "core_course_get_courses_by_field",
                "field": "category",
                "value": response[0]["id"],
            }

            response = await session.get(baseUrl, params=param_prodi_courses, ssl=False)
            result_course = await response.json()

            filtered_courses = [
                course for course in result_course["courses"] if active_semester in course["shortname"]
            ]

            tasks = []
            for course in filtered_courses:
                tasks.append(process_course(session, baseUrl, course, fakultas_sheets, fakultas, nama_prodi, backup_file))

                if len(tasks) % 100 == 0:
                    await asyncio.gather(*tasks)
                    tasks = []

            if tasks:
                await asyncio.gather(*tasks)

            processed_prodi.add(nama_prodi)
            print(nama_prodi)
            save_backup(backup_file, {"processed_prodi": processed_prodi, "fakultas_sheets": fakultas_sheets})

        if fakultas_sheets:
            with pd.ExcelWriter("course_reports_survey_TA241.xlsx") as writer:
                for fakultas, records in fakultas_sheets.items():
                    df = pd.DataFrame(records)
                    df.to_excel(writer, sheet_name=fakultas[:31], index=False)

        if os.path.exists(backup_file):
            os.remove(backup_file)

if __name__ == "__main__":
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=99bb1320ef22fc37619dd027659e8d94&moodlewsrestformat=json"
    asyncio.run(fetch_sikola_course())
