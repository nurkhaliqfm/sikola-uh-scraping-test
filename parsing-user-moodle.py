import json
import csv


def check_first_letter_and_second_digit(string):
    if string:
        if string[0].isalpha() and string[1].isdigit():
            return True
    return False


def check_first_five_digits(string):
    if len(string) >= 5 and string[:5].isdigit():
        return True
    return False


with open("data/mdl_user.json", "r") as file:
    data = json.load(file)

mahasiswa = []
pegawai = []

for user in data:
    if check_first_letter_and_second_digit(user["username"]):
        nama_lengkap = user["firstname"]
        email = user["email"]
        data_mahasiswa = {"nama_lengkap": nama_lengkap, "email": email}
        mahasiswa.append(data_mahasiswa)
    elif check_first_five_digits(user["username"]):
        nama_lengkap = user["firstname"]
        email = user["email"]
        data_pegawai = {"nama_lengkap": nama_lengkap, "email": email}
        pegawai.append(data_pegawai)

# CSV file path
csv_file = "Mahasiswa.csv"
csv_filePegawai = "Pegawai.csv"

# Writing data to CSV file
with open(csv_file, mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["nama_lengkap", "email"])

    # Write header
    writer.writeheader()

    # Write data
    for row in mahasiswa:
        writer.writerow(row)

# Writing data to CSV file
with open(csv_filePegawai, mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["nama_lengkap", "email"])

    # Write header
    writer.writeheader()

    # Write data
    for row in pegawai:
        writer.writerow(row)

print("CSV file has been created successfully.")
