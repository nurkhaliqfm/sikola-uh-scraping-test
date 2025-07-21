import csv
import pandas as pd

file = "data/CourseReport2/combined_data.csv"
with open(file, "r") as f:
    data = csv.reader(f, delimiter=";")

    dataLog = {}
    for item in data:
        if not item[0] == "Program Studi":
            if item[0] not in dataLog:
                dataLog[item[0]] = {"course": 0, "hasmateri": 0, "fullmateri": 0}

            dataLog[item[0]]["course"] += 1
            
            print(item)

            # Extract all relevant columns
            columns = [item[4], item[6], item[8], item[10], item[12], item[14], item[16], item[18],
                       item[20], item[22], item[24], item[26], item[28], item[30], item[32], item[34]]
            
            # Filter out non-integer values
            int_columns = []
            for col in columns:
                try:
                    int_columns.append(int(col))
                except ValueError:
                    int_columns.append(0)  # or handle differently if needed

            # If any column has a value greater than 0
            if any(val > 0 for val in int_columns):
                dataLog[item[0]]["hasmateri"] += 1

            # If all columns have values greater than 0
            if all(val > 0 for val in int_columns):
                dataLog[item[0]]["fullmateri"] += 1

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
            "PROGRAM STUDI",
            "JUMLAH KELAS",
            "JML KELAS PUNYA MATERI",
            "JML KELAS PUNYA MATERI 16 PERTEMUAN",
        ],
    )
    df.to_csv("UPDATE-COURSE-DATA.csv", index=False, header=True, sep=";")
