import pandas as pd

# Fungsi untuk membagi data ke beberapa sheet
def split_data_to_sheets(file_path, output_file, rows_per_sheet=250):
    # Baca data dari file
    df = pd.read_excel(file_path)
    
    # Hitung jumlah sheet yang dibutuhkan
    total_rows = len(df)
    num_sheets = (total_rows // rows_per_sheet) + (1 if total_rows % rows_per_sheet != 0 else 0)
    
    # Buat writer untuk menulis ke Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for i in range(num_sheets):
            start_row = i * rows_per_sheet
            end_row = start_row + rows_per_sheet
            sheet_df = df.iloc[start_row:end_row]
            sheet_name = f'Sheet{i+1}'
            sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f'Successfully split data into {num_sheets} sheets in {output_file}')

# Path ke file input dan output
input_file = 'data/MK/all_kelas_2.xlsx'  # Ganti dengan path file input Anda
output_file = 'data/MK/all_kelas_split.xlsx'  # Ganti dengan path file output Anda

# Panggil fungsi untuk membagi data ke beberapa sheet
split_data_to_sheets(input_file, output_file)
