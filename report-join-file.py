import glob
import json

allFolderDate = glob.glob(f"07-13-04-raw/*")

for folderDate in allFolderDate:
    selectedFolderDateDosen = glob.glob(f"{folderDate}/dosen/*.json")
    for dosenCourse in selectedFolderDateDosen:
        print(dosenCourse)

        with open(dosenCourse, "r") as f:
            data = f.read()

        loaded_data = json.loads(data)
        print(loaded_data[0]["users"])
