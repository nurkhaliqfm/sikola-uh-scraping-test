import csv
import pandas as pd

file = "data/DataExternal/x.csv"
with open(file, "r") as f:
    data = csv.reader(f, delimiter=",")

    dataLog = {}
    for item in data:
        if not item[0] == "PROGRMA STUDI":
            if item[0] not in dataLog:
                dataLog[item[0]] = {"course": 0, "updated": 0}

            dataLog[item[0]]["course"] += 1

            p1 = item[4]
            p2 = item[6]

            if int(p1) > 0:
                dataLog[item[0]]["updated"] += 1

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
            "PROGRAM STUDI",
            "JUMLAH KELAS",
            "TERUPDATE",
        ],
    )
    df.to_csv("UPDATE-COURSE-DATA.csv", index=False, header=True, sep=";")
