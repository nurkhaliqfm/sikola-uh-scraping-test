import asyncio
import json
import os
import requests

# async def get_dosen():
#     TOKEN_USER = os.getenv("TOKEN_USER")
#     url = "http://api.devs.unhas.ac.id/sikola-service/list-dosen-neosia/"
#     headers = {
#     }
    
#     response = requests.request("GET", url, headers=headers)
#     data = response.json()
#     total_results = data.get('totalResults', 0)
    
#     items_per_page = data.get('itemsPerPage', 0)

#     start_index = 0
#     all_data = {}

#     for start_index in range(0, total_results, items_per_page):
#         params = {
#             'startIndex': start_index
#         }

#         response = requests.request("GET", url, headers=headers, params=params)
#         data = response.json()
#         entries = data.get('entry', [])
        
#         for entry in entries:
#             nip = entry.get('nip')
#             id_value = entry.get('id')
#             if nip:
#                 all_data[nip] = id_value
#     with open('data/DataExternal/Dictionary_Dosen_2.json', 'w') as f:
#         json.dump(all_data, f)

async def get_mahasiswa():
    url = "http://api.devs.unhas.ac.id/sikola-service/list-mahasiswa-neosia/"
    headers = {
    }
    
    response = requests.request("GET", url, headers=headers)
    data = response.json()
    total_results = data.get('totalResults', 0)
    
    items_per_page = data.get('itemsPerPage', 0)

    start_index = 0
    all_data_mhs = {}

    for start_index in range(0, total_results, items_per_page):
        params = {
            'startIndex': start_index
        }

        response = requests.request("GET", url, headers=headers, params=params)
        data = response.json()
        entries = data.get('entry', [])

        for entry in entries:
            nim = entry.get('nim')
            id_value = entry.get('id')
            if nim:
                all_data_mhs[nim] = id_value
    with open('data/DataExternal/Dictionary_Mahasiswa_2.json', 'w') as f:
        json.dump(all_data_mhs, f)

# async def main():
#     await get_dosen()
#     await get_mahasiswa()

if __name__ == '__main__':
    asyncio.run(get_mahasiswa())
    print("Succcessfully")