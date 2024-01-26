import os
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

USERNAME = os.getenv("SIKOLA_USERNAME")
PASSWORD = os.getenv("SIKOLA_PASSWORD")

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")

dataMatakulihaSikola = pd.read_csv(
    f"data/scraping/Scraping-Matkul-Sikola-UH.csv", sep=";"
)

logScraping = pd.read_csv(f"log.csv", sep=";")

dataFound = logScraping.loc[0, "Found"]
dataNotFound = logScraping.loc[0, "NotFound"]
isFound = ""
scrapingResult = []


for dataIndex in range(logScraping.loc[0, "Current"], len(dataMatakulihaSikola)):
    try:
        courseNumber = dataMatakulihaSikola.loc[dataIndex, "No"]
        courseLink = dataMatakulihaSikola.loc[dataIndex, "Link Matkul"]
        courseName = dataMatakulihaSikola.loc[dataIndex, "Name"]
        courseCode = dataMatakulihaSikola.loc[dataIndex, "Kode Matkul"]
        courseKategori = dataMatakulihaSikola.loc[dataIndex, "Kategori Matkul"]

        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options,
        )

        driver.get("https://sikola.unhas.ac.id/")

        eLoginUsername = driver.find_element(By.ID, "login")
        eLoginUsername.clear()
        eLoginUsername.send_keys(USERNAME)
        eLoginPassword = driver.find_element(By.ID, "password")
        eLoginPassword.clear()
        eLoginPassword.send_keys(PASSWORD)

        eLoginButton = driver.find_element(By.XPATH, "//button[@name='submitAuth']")
        eLoginButton.click()

        driver.get(
            f"https://sikola.unhas.ac.id/main/exercise/exercise.php?cidReq={courseCode}&id_session=0&gradebook=0&origin=&gidReq=0"
        )

        # driver.save_screenshot(f"data/image/{courseCode}-{courseName}.png")

        try:
            eMatakuliahQuizTable = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//form[@id='form_exercises_cat_0_id']")
                )
            )

            eTableListQuiz = driver.find_element(
                By.XPATH,
                "//table[@class='table table-hover table-striped table-bordered data_table']",
            ).get_attribute("innerHTML")

            tableBodyParser = BeautifulSoup(eTableListQuiz, "html.parser")
            listItemTable = tableBodyParser.find_all("tr")
            isFound = "Found"
            dataFound += 1

            dataTablePage = [
                courseNumber,
                courseLink,
                courseName,
                courseCode,
                courseKategori,
                isFound,
            ]
            scrapingResult.append(dataTablePage)

        except:
            isFound = "Not Found"

            dataTablePage = [
                courseNumber,
                courseLink,
                courseName,
                courseCode,
                courseKategori,
                isFound,
            ]
            scrapingResult.append(dataTablePage)
            dataNotFound += 1

    finally:
        print(f"current index = {dataIndex}")
        df = pd.DataFrame(
            scrapingResult,
            columns=[
                "No",
                "Link Matkul",
                "Name",
                "Kode Matkul",
                "Kategori Matkul",
                "Is Found",
            ],
        )
        df.to_csv("Matkul-Quiz-Status-Sikola-UH.csv", index=False, header=True, sep=";")

        dfLog = pd.DataFrame(
            [[dataIndex, dataFound, dataNotFound]],
            columns=[
                "Current",
                "Found",
                "NotFound",
            ],
        )

        dfLog.to_csv("log.csv", index=False, header=True, sep=";")
