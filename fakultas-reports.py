import csv
import json
import pandas as pd

file = "data/DataExternal/prodi.json"
fileMentah = "data/DataExternal/x.csv"

with open(file, "r") as f:
    data = f.read()

    dataJson = json.loads(data)
    dataExpFakultas = {}
    for prodi in dataJson["prodis"]:
        namaProdi = prodi["nama_resmi"]
        namaFakultas = prodi["fakultas"]["nama_resmi"]
        if not namaProdi in namaFakultas:
            dataExpFakultas[namaProdi] = namaFakultas

    with open(fileMentah, "r") as f:
        dataMentah = csv.reader(f, delimiter=",")

        dataLog = {}
        for item in dataMentah:
            if not item[0] == "PROGRMA STUDI":
                if dataExpFakultas[item[0]] not in dataLog:
                    dataLog[dataExpFakultas[item[0]]] = {"course": 0, "updated": 0}

                dataLog[dataExpFakultas[item[0]]]["course"] += 1

                p1 = item[4]
                p2 = item[6]

                if int(p1) > 0:
                    dataLog[dataExpFakultas[item[0]]]["updated"] += 1

        dataExp = []
        for item in dataLog:
            namaProdi = item
            jumlahKelas = dataLog[item]["course"]
            jumlahKelasUpdated = dataLog[item]["updated"]
            dataExpItem = [namaProdi, jumlahKelas, jumlahKelasUpdated]
            dataExp.append(dataExpItem)

        df = pd.DataFrame(
            dataExp,
            columns=[
                "FAKULTAS",
                "JUMLAH KELAS",
                "TERUPDATE",
            ],
        )

        df.to_csv("UPDATE-COURSE-DATA-FAKULTAS.csv", index=False, header=True, sep=";")
