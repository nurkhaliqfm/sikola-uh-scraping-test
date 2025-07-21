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


# Fungsi untuk memuat progres dari file backup
def load_backup(file_name):
    if os.path.exists(file_name):
        with open(file_name, "rb") as f:
            return pickle.load(f)
    return None


# Fungsi untuk menyimpan progres ke file backup
def save_backup(file_name, data):
    with open(file_name, "wb") as f:
        pickle.dump(data, f)

async def process_course(session, baseUrl, course, data_reports, nama_prodi, fakultas):
    """
    Process a course to calculate the number of students and prepare report data.
    """
    courseid = course["id"]

    # Fetch enrolled users
    param_course = {
        "wsfunction": "core_enrol_get_enrolled_users",
        "courseid": courseid,
    }

    try:
        response = await session.get(baseUrl, params=param_course, ssl=False)
        users = await response.json()

        # Filter students (mahasiswa) from enrolled users
        mahasiwas = [
            user for user in users if any(grup["name"] == "MAHASISWA" for grup in user.get("groups", []))
        ]
        jumlah_mhs = len(mahasiwas)

        # Append to report
        data_reports.append(
            {
                "Nama Prodi": nama_prodi,
                "Nama Fakultas": fakultas,
                "Nama Kelas": course["fullname"],
                "Jumlah Mahasiswa": jumlah_mhs,
            }
        )
    except Exception as e:
        print(f"Error processing course {course['fullname']} (ID: {courseid}): {e}")


async def fetch_sikola_course():
    async with aiohttp.ClientSession() as session:
        active_semester = "TA241"
        kwu_keywords = ["KEWIRAUSAHAAN", "ENTERPRENEUR"]
        data_reports = []
        backup_file = "backup_course_data.pkl"

        # Load fakultas and prodi data
        with open("data/prodi_semester.json", "r", encoding="utf-8") as faculty_file:
            datafakultasProdi = json.load(faculty_file)

        for prodi in datafakultasProdi["prodis"]:
            nama_prodi = prodi["nama_resmi"]
            fakultas = prodi["fakultas"]["nama_resmi"]

            # Fetch categories by prodi name
            param_prodi = {
                "wsfunction": "core_course_get_categories",
                "criteria[0][key]": "name",
                "criteria[0][value]": nama_prodi,
            }
            response = await session.get(baseUrl, params=param_prodi, ssl=False)
            categories = await response.json()
            if not categories:
                continue

            # Fetch courses in the category
            param_prodi_courses = {
                "wsfunction": "core_course_get_courses_by_field",
                "field": "category",
                "value": categories[0]["id"],
            }
            response = await session.get(baseUrl, params=param_prodi_courses, ssl=False)
            result_course = await response.json()

            # Filter courses by semester and keywords
            filtered_courses = [
                course for course in result_course["courses"]
                if active_semester in course["shortname"] and any(kwu in course["fullname"].upper() for kwu in kwu_keywords)
            ]

            # Process courses concurrently
            tasks = [
                process_course(session, baseUrl, course, data_reports, nama_prodi, fakultas)
                for course in filtered_courses
            ]
            await asyncio.gather(*tasks)

        # Generate Excel report
        df = pd.DataFrame(data_reports)
        df.to_excel("course_reports_kwu_ta2321.xlsx", index=False)

        print("Report saved to course_reports_kwu_ta232.xlsx")


if __name__ == "__main__":
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"
    asyncio.run(fetch_sikola_course())
