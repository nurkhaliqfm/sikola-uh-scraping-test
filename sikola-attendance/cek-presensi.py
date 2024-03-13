from flask import Flask, request, jsonify
import os
import csv
import requests


app = Flask(__name__)

@app.route('/attendance', methods=['GET'])
def get_attendance():
    id_kelas = request.args.get('id_kelas')
    not_in_mahasiswa = request.args.get('not_in_mahasiswa')
    not_in_dosen = request.args.get('not_in_dosen')

    date_folder = "2024-03-09"
    dosen_folder = f"data/attendanceRaw/{date_folder}/dosen"
    mahasiswa_folder = f"data/attendanceRaw/{date_folder}/mahasiswa"

    dosen_files = os.listdir(dosen_folder)
    mahasiswa_files = os.listdir(mahasiswa_folder)

    dosen_id_kelas = [filename.split(".")[0] for filename in dosen_files]
    mahasiswa_id_kelas = [filename.split(".")[0] for filename in mahasiswa_files]

    if not_in_mahasiswa:
        not_in_mahasiswa = [filename for filename in dosen_id_kelas if filename not in mahasiswa_id_kelas]
        with open(f"data/cekPresensi/notInMahasiswa-{date_folder}.csv", "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["id_kelas"])
            writer.writerows([[id_kelas] for id_kelas in not_in_mahasiswa])

    if not_in_dosen:
        not_in_dosen = [filename for filename in mahasiswa_id_kelas if filename not in dosen_id_kelas]
        with open(f"data/cekPresensi/notInDosen-{date_folder}.csv", "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["id_kelas"])
            writer.writerows([[id_kelas] for id_kelas in not_in_dosen])
    
    response = requests.get(f"https://api.neosia.unhas.ac.id/apiadmin_mkpk/pertemuan", params={"filters": {"id_kelas": id_kelas}})
    data = response.json()

    return jsonify({"message": "Done.", "data": data})
    # return jsonify({"message": "Done."})

if __name__ == '__main__':
    app.run(debug=True)
