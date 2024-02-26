import csv
import json

with open("data/DataExternal/Data_Mahasiswa_Neosia.csv", "r") as csvfile:
    csvreader = csv.reader(csvfile)
    json_file_path = "data/DataExternal/Dictionary_Mahasiswa.json"
    data_mahasiswa = {}
    for row in csvreader:
        data = {row[2].upper(): row[0]}
        data_mahasiswa.update(data)

    with open(json_file_path, "w") as json_file:
        json.dump(data_mahasiswa, json_file, indent=4)
