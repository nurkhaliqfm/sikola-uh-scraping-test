import csv
import json

with open("data/DataExternal/data_dosen_neosia.csv", "r") as csvfile:
    csvreader = csv.reader(csvfile)
    json_file_path = "data/DataExternal/Dictionary_Dosen.json"
    data_dosen = {}
    for row in csvreader:
        data = {row[3].upper(): row[0]}
        data_dosen.update(data)

    with open(json_file_path, "w") as json_file:
        json.dump(data_dosen, json_file, indent=4)
