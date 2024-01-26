import pandas as pd

dataMatakulihaSikola = pd.read_csv(
    f"data/scraping/Matkul-Quiz-Status-Sikola-UH.csv", sep=";"
)


scrapingResult = []
courseFoundQuiz = 0

for dataIndex in range(len(dataMatakulihaSikola)):
    try:
        statusCourse = dataMatakulihaSikola.loc[dataIndex, "Is Found"]
        if statusCourse == "Found":
            courseNumber = dataMatakulihaSikola.loc[dataIndex, "No"]
            courseLink = dataMatakulihaSikola.loc[dataIndex, "Link Matkul"]
            courseName = dataMatakulihaSikola.loc[dataIndex, "Name"]
            courseCode = dataMatakulihaSikola.loc[dataIndex, "Kode Matkul"]
            courseKategori = dataMatakulihaSikola.loc[dataIndex, "Kategori Matkul"]

            courseFoundQuiz += 1
            dataTablePage = [
                courseNumber,
                courseLink,
                courseName,
                courseCode,
                courseKategori,
            ]
            scrapingResult.append(dataTablePage)

    finally:
        df = pd.DataFrame(
            scrapingResult,
            columns=[
                "No",
                "Link Matkul",
                "Name",
                "Kode Matkul",
                "Kategori Matkul",
            ],
        )
        df.to_csv("Matkul-Quiz-Found.csv", index=False, header=True, sep=";")
