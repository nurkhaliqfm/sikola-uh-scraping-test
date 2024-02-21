import phpserialize
import json

# Read serialized data from .dat file
with open("data/DataExternal/result-parsing-courseInbound.dat", "rb") as file:
    serialized_data = file.read()

# Deserialize the data
deserialized_data = phpserialize.loads(serialized_data)

x = 0


def decode_dict(input_dict):
    decoded_dict = {}
    for key, value in input_dict.items():
        if isinstance(key, bytes):
            key = key.decode("utf-8", errors="ignore")
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="ignore")
        elif isinstance(value, dict):
            value = decode_dict(value)
        decoded_dict[key] = value
    return decoded_dict


allData = []
if isinstance(deserialized_data, dict):
    converted_dict = {}
    for key, value in deserialized_data.items():
        data = decode_dict(value)
        print(data)
        item = {
            "nama_kelas": data["nama_kelas"],
            "nim_mahas": data["nim_mahasiswa"],
            "results": data["result"],
        }
        allData.append(item)
with open("data/DataExternal/converted_data.json", "w") as json_file:
    json.dump(allData, json_file)
