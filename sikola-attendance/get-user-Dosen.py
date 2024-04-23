import requests
import os
import json
import asyncio
import aiohttp
import csv
from dotenv import load_dotenv

load_dotenv()


API_NEOSIA = os.getenv('API_NEOSIA')

async def fetch_data(user_id):
    url = f"https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json&wsfunction=core_user_get_users_by_field&field=id&values[0]={user_id}"
    try:
      async with aiohttp.ClientSession() as session:
          async with session.get(url, ssl=False) as response:
              if response.headers['Content-Type'] == 'application/json':
                  dataDosen = await response.json()
                  return dataDosen
              else:
                  print(f"Unexpected content type received for user {user_id}")
                  return None
    except aiohttp.ClientConnectorError as e:
        print(f"Error fetching data for user {user_id}: {e}")
        return None
async def process_data(user):
    user_id = user['id']
    for _ in range(5):
        try:
            dataDosen = await fetch_data(user_id)
            if dataDosen[0]['username'].startswith('1'):
                print("Non-praktisi-1", user_id)
                os.makedirs(f"data/Dosen-1/", exist_ok=True)
                with open(f"data/Dosen-1/{user_id}.json", "w") as f:
                    json.dump(dataDosen, f, indent=4)
            if dataDosen[0]['username'].startswith('7'):
                print("Non-praktisi-7", user_id)
                os.makedirs(f"data/Dosen-7/", exist_ok=True)
                with open(f"data/Dosen-7/{user_id}.json", "w") as f:
                    json.dump(dataDosen, f, indent=4)
            if not dataDosen[0]['username'].isdigit():
                print("praktisi", user_id)
                os.makedirs(f"data/DosenPraktisi/", exist_ok=True)
                with open(f"data/DosenPraktisi/{user_id}.json", "w") as f:
                    json.dump(dataDosen, f, indent=4)
            break
        except Exception as e:
            print(f"An error occurred during processing data for user {user_id}: {e}")
async def main():
    tasks = []
    for foldername in os.listdir(folder_path):
        if start_date <= foldername <= end_date:
            folder_full_path = os.path.join(folder_path, foldername, "dosen")
            for filename in os.listdir(folder_full_path):
                if filename.endswith(".json"):
                    with open(os.path.join(folder_full_path, filename), 'r') as file:
                        data = json.load(file)
                        for user in data[0]['users']:
                            tasks.append(process_data(user))
    await asyncio.gather(*tasks)



async def fetchPraktisi():
    headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImZjMWIyMGI5ZDFmNDQ3OTYxNzNkZmIxNTVkYTBkMGE4ZjhmODA2MzQ2NmEwZjk3NTk2NWY1ZmJjM2I3ODc1ZGQ5MjA0NzQxY2Y1ZTFmNzkyIn0.eyJhdWQiOiIyIiwianRpIjoiZmMxYjIwYjlkMWY0NDc5NjE3M2RmYjE1NWRhMGQwYThmOGY4MDYzNDY2YTBmOTc1OTY1ZjVmYmMzYjc4NzVkZDkyMDQ3NDFjZjVlMWY3OTIiLCJpYXQiOjE3MTMxNjAwODIsIm5iZiI6MTcxMzE2MDA4MiwiZXhwIjoxNzEzNTkyMDgyLCJzdWIiOiI4NTQ5NiIsInNjb3BlcyI6WyIqIl19.bDZQLsWq1R-7zveRDxoQVusLP7ztMx5ndgvGBGXcfGWxjONZ-TnedPtCZJUqvQUEKh9SykAndIx9op6aO6ceHzc0EjvsakvRKDWbkPirDwWtPvQ3iPSShhbYhYeu_vqiqZtLfQee4Gef0skAWBahIQsvN8cWUw9JEhddi1z91vwIzx_w0AfJPbnQTGMG3DNUlslWTVakh_mgfzbMPqutfKW9K2W1WrIGt8lFla0KkGJYcVARvXjwCR6VMYY477lkEf4gHxcodeR5oleFy8L8DplDRs15_gSzuGJtnjH5mi_zjfgHGZ7nVxaIiVnS-Q6DjJCnhdi5mnppvf1zQP5BJfXiBoNN_CD4E143qddpq76P65SUNUXBMqJdX5IFO92aHJdBEmSAxbHvT1A81cDLWs1x1VsuBtFOFy9K3gdZnwwieKdmGHWA1t2yUcivyO3Lq-jwA7QDYCgNPwfKXYgkDAxCUXNo-2riZ5n4YG0w52368Kaht8reEY6grBC76451_JJNTF43MMghu8GZT7TN5jWFbtZ_HKj_LIvz5Ml4YH5KSzATM4JbTbW65n5wswaCLGWqW-xlEGq6FTAIaim8mZGyfMCQpabIWKV_XFCinY0byBtQ38F43CNiz1eZaltfo5Fv34hRY_fzSkpxOj9X4PubES64kwC31hlBUIGK-dA'
    }

          
    folder_praktisi = 'data/Dosen-7/'
    
    result_data = []
    tasks = []

    for filename in os.listdir(folder_praktisi):
      if filename.endswith(".json"):
        with open(os.path.join(folder_praktisi, filename), 'r') as file:
            data = json.load(file)
            if 'idnumber' in data[0]:
                idnumber= data[0]['idnumber']
                fullname= data[0]['fullname']
                print(idnumber)
                user_id = filename.split(".json")[0]
                url = f"https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json&wsfunction=core_enrol_get_users_courses&userid={user_id}"
                try:
                  async with aiohttp.ClientSession() as session:
                      async with session.get(url, ssl=False) as response:
                          if response.headers['Content-Type'] == 'application/json':
                              dataDosen = await response.json()
                              for course in dataDosen:
                                
                                for _ in range(2):
                                  try:
                                    id_kelas = course['shortname'].split('-')[1]
                                    print(course['fullname'], idnumber, id_kelas)
                                    async with session.get(
                                        f"{API_NEOSIA}/admin_mkpk/dosen/input_nilai/kelas_kuliah/{id_kelas}",
                                        headers=headers,
                                        ssl=False
                                    ) as response:
                                        response_data = await response.json()
                                    
                                    async with session.get(
                                        f"{API_NEOSIA}/admin_mkpk/prodi",
                                        headers=headers,
                                        ssl=False
                                    ) as response_fakultas:
                                        response_fakultas_data = await response_fakultas.json()

                                    id_prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['id']
                                    nama_kelas = response_data['kelasKuliah']['nama']
                                    prodi = response_data['kelasKuliah']['prodi_semester']['prodi']['nama_resmi']
                                    nama_fakultas = next((p['fakultas']['nama_resmi'] for p in response_fakultas_data['prodis'] if p['id'] == id_prodi), None)

                                    result_data.append([idnumber, fullname, nama_kelas, prodi, nama_fakultas])
                                    break                                  
                                  except Exception as e:
                                    print(f"An error occurred during processing data for course {course['fullname']}: {e}")
                                
                              
                          else:
                              print(f"Unexpected content type received for user {user_id}")
                              return None
                except aiohttp.ClientConnectorError as e:
                    print(f"Error fetching data for user {user_id}: {e}")
                    return None
    with open(f"{folder_praktisi}/DosenNIK.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["username","nama_dosen", 'nama_kelas', 'prodi', 'nama_fakultas'])
        writer.writerows(result_data)
        
   
              
              
                                
if __name__ == "__main__":
  
 
  start_date = "2024-03-04"
  end_date = "2024-03-10"
  folder_path = "data/attendanceRaw/"
  
  
  
  asyncio.run(fetchPraktisi())
# for foldername in os.listdir(folder_path):
#     if start_date <= foldername <= end_date:
#         folder_full_path = os.path.join(folder_path, foldername, "dosen")
#         for filename in os.listdir(folder_full_path):
#           if filename.endswith(".json"):
#               with open(os.path.join(folder_full_path, filename), 'r') as file:
#                   data = json.load(file)
#                   for user in data[0]['users']:
#                       user_id = user['id']
#                       url = f"https://sikola-v2.unhas.ac.id/webservice/rest/server.php?wstoken=07480e5bbb440a596b1ad8e33be525f8&moodlewsrestformat=json&wsfunction=core_user_get_users_by_field&field=id&values[0]={user_id}"

#                       payload = {}
#                       headers = {}
#                       response = requests.request("GET", url, headers=headers, data=payload)
#                       dataDosen = response.json()
                      
#                       # print(dataDosen[0]['username'])
                      
#                       if dataDosen[0]['username'].isdigit():
#                           os.makedirs(f"data/Dosen/", exist_ok=True)
#                           with open(f"data/Dosen/{user_id}.json", "w") as f:
#                               json.dump(dataDosen, f, indent=4)
#                       else:
#                           os.makedirs(f"data/DosenPraktisi/", exist_ok=True)
#                           with open(f"data/DosenPraktisi/{user_id}.json", "w") as f:
#                               json.dump(dataDosen, f, indent=4)
                      
                      
