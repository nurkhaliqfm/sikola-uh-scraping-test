import csv
import json
import pandas as pd

file = "data/DataExternal/prodi.json"
fileMentah = "data/CourseReport/combined_data.csv"

with open(file, "r", encoding="utf-8") as f:
    data = f.read()
    

    dataJson = json.loads(data)
    dataExpFakultas = {}
    for prodi in dataJson["prodis"]:
        namaProdi = prodi["nama_resmi"]
        namaFakultas = prodi["fakultas"]["nama_resmi"]
        if not namaProdi in namaFakultas:
            dataExpFakultas[namaProdi] = namaFakultas

    with open(fileMentah, "r", encoding="utf-8") as f:
        dataMentah = csv.reader(f, delimiter=";")

        print(dataMentah)
        dataLog = {}
        for item in dataMentah:
            if not item[0] == "Program Studi":
                if dataExpFakultas[item[0]] not in dataLog:
                    dataLog[dataExpFakultas[item[0]]] = {
                        "course": 0,
                        "hasmateri": 0,
                        "fullmateri": 0,
                    }

                dataLog[dataExpFakultas[item[0]]]["course"] += 1

                p1 = item[4]
                p2 = item[6]
                p3 = item[8]
                p4 = item[10]
                p5 = item[12]
                p6 = item[14]
                p8 = item[16]
                p7 = item[18]
                p9 = item[20]
                p10 = item[22]
                p11 = item[24]
                p12 = item[26]
                p13 = item[28]
                p14 = item[30]
                p15 = item[32]
                p16 = item[34]

                # if int(p1) > 0:
                #     dataLog[dataExpFakultas[item[0]]]["updated"] += 1
                if (
                    int(p1) > 0
                    or int(p2) > 0
                    or int(p3) > 0
                    or int(p4) > 0
                    or int(p5) > 0
                    or int(p6) > 0
                    or int(p7) > 0
                    or int(p8) > 0
                    or int(p9) > 0
                    or int(p10) > 0
                    or int(p11) > 0
                    or int(p12) > 0
                    or int(p13) > 0
                    or int(p14) > 0
                    or int(p15) > 0
                    or int(p16) > 0
                ):
                    dataLog[dataExpFakultas[item[0]]]["hasmateri"] += 1
                if (
                    int(p1) > 0
                    and int(p2) > 0
                    and int(p3) > 0
                    and int(p4) > 0
                    and int(p5) > 0
                    and int(p6) > 0
                    and int(p7) > 0
                    and int(p8) > 0
                    and int(p9) > 0
                    and int(p10) > 0
                    and int(p11) > 0
                    and int(p12) > 0
                    and int(p13) > 0
                    and int(p14) > 0
                    and int(p15) > 0
                    and int(p16) > 0
                ):
                    dataLog[dataExpFakultas[item[0]]]["fullmateri"] += 1

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
