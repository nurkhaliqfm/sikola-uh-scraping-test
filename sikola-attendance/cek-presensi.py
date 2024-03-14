import os
import json
import csv
import shutil

date_folder = "2024-03-10"
dosen_folder = f"data/attendanceRaw/{date_folder}/dosen"
mahasiswa_folder = f"data/attendanceRaw/{date_folder}/mahasiswa"
result_folder_dosen = f"data/cekPresensi"
result_folder_mahasiswa = f"data/cekPresensi"

os.makedirs(result_folder_dosen, exist_ok=True)
os.makedirs(result_folder_mahasiswa, exist_ok=True)

# Get the list of files in each folder
dosen_files = os.listdir(dosen_folder)
mahasiswa_files = os.listdir(mahasiswa_folder)


dosen_id_kelas = [filename.split(".")[0] for filename in dosen_files]
mahasiswa_id_kelas = [filename.split(".")[0] for filename in mahasiswa_files]

# Check files in dosen folder but not in mahasiswa folder
not_in_mahasiswa = [filename for filename in dosen_id_kelas if filename not in mahasiswa_id_kelas]
with open(os.path.join(result_folder_mahasiswa, f"notInMahasiswa-{date_folder}.csv"), "w", newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["id_kelas"])
    writer.writerows([[id_kelas] for id_kelas in not_in_mahasiswa])

# Check files in mahasiswa folder but not in dosen folder
not_in_dosen = [filename for filename in mahasiswa_id_kelas if filename not in dosen_id_kelas]
with open(os.path.join(result_folder_dosen, f"notInDosen-{date_folder}.csv"), "w", newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["id_kelas"])
    writer.writerows([[id_kelas] for id_kelas in not_in_dosen])

print("Done.")
