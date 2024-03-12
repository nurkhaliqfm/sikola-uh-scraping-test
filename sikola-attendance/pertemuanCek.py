import os
import json
import csv

date_folder = "2024-03-08"
dosen_folder = f"data/absensi/{date_folder}/dosen"
mahasiswa_folder = f"data/absensi/{date_folder}/mahasiswa"

output_folder = f"data/pertemuanKeCek/{date_folder}"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

def json_to_csv(input_folder, output_file):
    with open(output_file, "w", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id_kelas_kuliah', 'nama_matakuliah', 'tanggal_rencana', 'pertemuan_ke'])
        writer.writeheader()
        for file_name in os.listdir(input_folder):
            input_path = os.path.join(input_folder, file_name)
            with open(input_path, "r") as file:
                data = json.load(file)
                for item in data:
                    writer.writerow({
                        'id_kelas_kuliah': item['pertemuan']['id_kelas_kuliah'],
                        'nama_matakuliah': item['nama_matakuliah'],
                        'tanggal_rencana': item['pertemuan']['tanggal_rencana'],
                        'pertemuan_ke': item['pertemuan']['pertemuan_ke']
                    })

# Convert dosen JSON files to CSV
json_to_csv(dosen_folder, os.path.join(output_folder, "dosen.csv"))

# Convert mahasiswa JSON files to CSV
json_to_csv(mahasiswa_folder, os.path.join(output_folder, "mahasiswa.csv"))

print("Conversion completed.")
