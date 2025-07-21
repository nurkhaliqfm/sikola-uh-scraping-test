import aiohttp
import asyncio
import glob
import os
import requests
import json
import pickle
import pandas as pd
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

load_dotenv()

# Disable InsecureRequestWarning
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)




async def fetch_sikola_course():
    async with aiohttp.ClientSession() as session:
        active_semester = "TA241"
        data_reports = []

        with open("data/prodi_semester.json", "r", encoding="utf-8") as faculty:
            datafakultasProdi = faculty.read()

        datafakultas = json.loads(datafakultasProdi)

        for prodi in datafakultas["prodis"]:
            nama_prodi = prodi["nama_resmi"]
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
                course
                for course in result_course["courses"]
                if active_semester in course["shortname"]
            ]

            total_courses = len(filtered_courses)
            no_active_modules = 0
            active_modules = 0
            no_attendance = 0
            with_attendance = 0

            for course in filtered_courses:
                courseid = course["id"]
                param_course = {
                    "wsfunction": "core_course_get_contents",
                    "courseid": courseid,
                }
                response = await session.get(baseUrl, params=param_course, ssl=False)
                contents = await response.json()

                # Check for active modules in sections other than 0
                has_other_modules = any(
                    section["section"] != 0 and any(mod["modname"] for mod in section["modules"])
                    for section in contents
                )
                if has_other_modules:
                    active_modules += 1
                else:
                    no_active_modules += 1

                # Check for attendance module
                has_attendance = False
                for section in contents:
                    for module in section["modules"]:
                        if module["modname"] == "attendance":
                            attendanceid = module["instance"]
                            param_attendance = {
                                "wsfunction": "mod_attendance_get_sessions",
                                "attendanceid": attendanceid,
                            }
                            session_response = await session.get(baseUrl, params=param_attendance, ssl=False)
                            sessions = await session_response.json()
                            if len(sessions) > 0:
                                has_attendance = True
                                break
                    if has_attendance:
                        break

                if has_attendance:
                    with_attendance += 1
                else:
                    no_attendance += 1

            # Calculate percentages
            attendance_percentage = (with_attendance / total_courses * 100) if total_courses else 0
            active_percentage = (active_modules / total_courses * 100) if total_courses else 0
            print(nama_prodi)

            # Add to report
            data_reports.append(
                [
                    nama_prodi,
                    fakultas,
                    total_courses,
                    no_active_modules,
                    active_modules,
                    no_attendance,
                    with_attendance,
                    attendance_percentage,
                    active_percentage,
                ]
            )

        # Create DataFrame and save to Excel
        df = pd.DataFrame(
            data_reports,
            columns=[
                "Nama Prodi",
                "Nama Fakultas",
                "Jumlah Total Course",
                "Jumlah Tidak Aktif",
                "Jumlah Aktif",
                "Jumlah Tanpa Attendance",
                "Jumlah Dengan Attendance",
                "Persentase Attendance (%)",
                "Persentase Aktif (%)",
            ],
        )

        df.to_excel("course_reports_TA241.xlsx", index=False)


if __name__ == "__main__":
    baseUrl = "https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json"
    asyncio.run(fetch_sikola_course())
