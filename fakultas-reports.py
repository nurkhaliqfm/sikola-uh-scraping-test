import csv
import json
import pandas as pd

file = "data/DataExternal/prodi.json"
fileMentah = "data/CourseReport2/combined_data.csv"

with open(file, "r", encoding="utf-8") as f:
    data = f.read()
    dataJson = json.loads(data)
    dataExpFakultas = {}
    for prodi in dataJson["prodis"]:
        namaProdi = prodi["nama_resmi"]
        namaFakultas = prodi["fakultas"]["nama_resmi"]
        dataExpFakultas[namaProdi] = namaFakultas

with open(fileMentah, "r", encoding="utf-8") as f:
    dataMentah = csv.reader(f, delimiter=";")
    next(dataMentah)  # Skip the header row

    dataLog = {}
    for item in dataMentah:
        namaProdi = item[0].strip()
        if namaProdi and namaProdi in dataExpFakultas:
            if dataExpFakultas[namaProdi] not in dataLog:
                dataLog[dataExpFakultas[namaProdi]] = {
                    "course": 0,
                    "hasmateri": 0,
                    "fullmateri": 0,
                }

            dataLog[dataExpFakultas[namaProdi]]["course"] += 1

            p_values = [item[i] for i in range(4, 35, 2)]

            has_materi = False
            full_materi = True

            for p in p_values:
                try:
                    if int(p) > 0:
                        has_materi = True
                    else:
                        full_materi = False
                except ValueError:
                    full_materi = False

            if has_materi:
                dataLog[dataExpFakultas[namaProdi]]["hasmateri"] += 1
            if full_materi:
                dataLog[dataExpFakultas[namaProdi]]["fullmateri"] += 1

dataExp = []
for item in dataLog:
    namaProdi = item
    jumlahKelas = dataLog[item]["course"]
    jumlahKelasUpdated = dataLog[item]["hasmateri"]
    jumlahKelasFullUpdated = dataLog[item]["fullmateri"]
    dataExpItem = [
        namaProdi,
        jumlahKelas,
        jumlahKelasUpdated,
        jumlahKelasFullUpdated,
    ]
    dataExp.append(dataExpItem)

df = pd.DataFrame(
    dataExp,
    columns=[
        "FAKULTAS",
        "JUMLAH KELAS",
        "JML KELAS PUNYA MATERI",
        "JML KELAS PUNYA MATERI 16 PERTEMUAN",
    ],
)

df.to_csv("UPDATE-COURSE-DATA-FAKULTAS.csv", index=False, header=True, sep=";")
