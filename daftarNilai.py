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

async def process_grade_items(session, course, data_reports):
    """
    Process grade items for a specific course and append the results to the report.
    """
    kelas_id = course["id_kelas"]
    keterangan = "Nilai Tidak Ada"
    

    url = f"https://sikola-v2.unhas.ac.id/grade/nilai-sikola.php?kelas_id={kelas_id}"
    headers = {
        "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTczMTkwMjgxMywianRpIjoiNmNmM2U3NzItMTZmNi00MTc3LTljNDktM2U1Y2ZmYjYwZDQwIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiJleGFtcGxlX3VzZXIiLCJuYmYiOjE3MzE5MDI4MTMsImNzcmYiOiJkNzdlZDg2NC1mMTY5LTQ1YjAtOGI2Zi05MWM4ZTYwNTJjNWUiLCJleHAiOjE3MzQ0OTQ4MTN9.CQxdPCmAPE6rAGJvVqs9Jxfu3XFHty-mbNox4b_FDbA"  # Load token securely
    }
    
    try:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            if data and isinstance(data, list):
                grade_items = data[0].get("gradeitems", [])
                item_names = []
                keterangan_list = []

                # Menghitung jumlah siswa yang memiliki nilai terinput untuk setiap grade item
                for item in grade_items:
                    item_name = (
                        "Course Total" if item.get("itemtype") == "course" else
                        item.get("itemname", "Unknown Item")
                    )
                    item_type = item.get("itemtype", "")
                    item_module = item.get("itemmodule", "")
                    student_count = sum(
                        1 for student in data if any(
                            gi.get("id") == item.get("id") and gi.get("graderaw") is not None
                            for gi in student.get("gradeitems", [])
                        )
                    )
                    
                    # Tambahkan ke rincian jika item bukan attendance dan bukan course
                    if item_module != "attendance" and item_type != "course" and student_count > 0:
                        keterangan_list.append(f"{item_name} : {student_count} Terinput")
                    item_types_in_class = set(gi.get("itemtype") for student in data for gi in student.get("gradeitems", []))
                    only_attendance_and_course = item_types_in_class.issubset({"attendance", "course"})

                    if only_attendance_and_course:
                        
                        graderaw_course_list = [
                            gi.get("graderaw")
                            for student in data
                            for gi in student.get("gradeitems", [])
                            if gi.get("itemtype") == "course" and gi.get("graderaw") is not None
                        ]
                        if graderaw_course_list and len(set(graderaw_course_list)) > 1:
                            for student in data:
                                graderaw_course = None
                                graderaw_attendance = None
                                for gi in student.get("gradeitems", []):
                                    if gi.get("itemtype") == "course":
                                        graderaw_course = gi.get("graderaw")
                                    if gi.get("itemmodule") == "attendance":
                                        graderaw_attendance = gi.get("graderaw")
                                if graderaw_course is not None and graderaw_attendance is not None and graderaw_course != graderaw_attendance:
                                    keterangan_list.append(
                                        f"Graderaw attendance ({graderaw_attendance}) berbeda dengan course ({graderaw_course}) untuk mahasiswa {student.get('userid', '')}"
                                    )
                                    
                    if not only_attendance_and_course:
                        # Ambil semua graderaw pada item 'course'
                        graderaw_course_list = [
                            gi.get("graderaw")
                            for student in data
                            for gi in student.get("gradeitems", [])
                            if gi.get("itemtype") == "course" and gi.get("graderaw") is not None
                        ]
                        # Jika graderaw course bervariasi (tidak seragam)
                        if graderaw_course_list and len(set(graderaw_course_list)) > 1:
                            for student in data:
                                graderaw_course = None
                                graderaw_attendance = None
                                for gi in student.get("gradeitems", []):
                                    if gi.get("itemtype") == "course":
                                        graderaw_course = gi.get("graderaw")
                                    if gi.get("itemmodule") == "attendance":
                                        graderaw_attendance = gi.get("graderaw")
                                if graderaw_course is not None and graderaw_attendance is not None and graderaw_course != graderaw_attendance:
                                    keterangan_list.append(
                                        f"Graderaw attendance ({graderaw_attendance}) berbeda dengan course ({graderaw_course}) untuk mahasiswa {student.get('userid', '')}"
                                    )
                    
                    item_names.append(item_name)
                if keterangan_list:
                    keterangan = 'Ada Nilai di Sikola (Belum Konfirmasi)'
                # keterangan = ", ".join(keterangan_list) if keterangan_list else "Nilai Tidak Ada"

                data_reports.append(
                    {
                        "Jenjang": course["Jenjang"],
                        "Fakultas": course["Fakultas"],
                        "Program Studi": course["Program Studi"],
                        "Nama Kelas": course["Nama Kelas"],
                        "ID Kelas": course["id_kelas"],
                        "Kode Mata Kuliah": course["Kode Mata Kuliah"],
                        "Nama Mata Kuliah": course["Nama Mata Kuliah"],
                        "Dosen Pengampuh": course["Dosen Pengampuh"],
                        "Dosen Koordinator": course["Dosen Koordinator"],
                        "jml_mahasiswa": course["jml_mahasiswa"],
                        "nilai_sudah_input_neosia": course["nilai_sudah_input"],
                        "persentase_neosia": course["persentase"],
                        "Nilai Terinput Sikola": len(data),
                        "Course ID": data[0].get("courseid", ""),
                        "Jumlah Grade Items": len(grade_items),
                        "Grade Items": ", ".join(item_names),
                        "Keterangan": keterangan
                    }
                )
    except Exception as e:
        print(f"Error processing course {kelas_id}: {e}")
        
        data_reports.append(
            {
                "Jenjang": course["Jenjang"],
                "Fakultas": course["Fakultas"],
                "Program Studi": course["Program Studi"],
                "Nama Kelas": course["Nama Kelas"],
                "ID Kelas": course["id_kelas"],
                "Kode Mata Kuliah": course["Kode Mata Kuliah"],
                "Nama Mata Kuliah": course["Nama Mata Kuliah"],
                "Dosen Pengampuh": course["Dosen Pengampuh"],
                "Dosen Koordinator": course["Dosen Koordinator"],
                "jml_mahasiswa": course["jml_mahasiswa"],
                "nilai_sudah_input_neosia": course["nilai_sudah_input"],
                "persentase_neosia": course["persentase"],
                "Nilai Terinput Sikola": 0,
                "Course ID": "",
                "Jumlah Grade Items": 0,
                "Grade Items": "",
                "Keterangan": "Nilai Tidak Ada"
            }
        )

async def fetch_course_data():
    async with aiohttp.ClientSession() as session:
        backup_file = "keterangan_ada_nilai_4.pkl"
        active_semester = "TA242"

        # Load progress from backup
        backup_data = load_backup(backup_file)
        processed_prodi = backup_data.get("processed_prodi", set())
        data_reports = backup_data.get("data_reports", [])

        # Load course names from Excel
        excel_file = "data/lists-242.xlsx"
        df_courses = pd.read_excel(excel_file)

        # Ensure consistent column names
        df_courses.columns = df_courses.columns.str.strip()
       

        # Iterate over courses
        for _, row in df_courses.iterrows():
            course = row.to_dict()
            
            await process_grade_items(session, course, data_reports)

        # Generate Excel report
        df = pd.DataFrame(data_reports)
        output_file = "keterangan_ada_nilai_4.xlsx"
        df.to_excel(output_file, index=False)
        print(f"Report saved to {output_file}")

        # Remove backup after success
        if os.path.exists(backup_file):
            os.remove(backup_file)

if __name__ == "__main__":
    asyncio.run(fetch_course_data())
