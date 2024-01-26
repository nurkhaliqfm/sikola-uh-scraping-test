import os
import pandas as pd
import time
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

dataMatakulihaSikola = pd.read_csv(f"data/scraping/Matkul-Quiz-Found.csv", sep=";")

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

        for itemIndex in range(1, len(listItemTable)):
            item = listItemTable[itemIndex].find_all("td")
            quizName = item[1].find("a").text.strip()
            
            quizDownloadButton = item[3].find_all("a")[7]
            quizDownloadFile = f"qti2_export_{quizDownloadButton["href"].split('exerciseId=')[1].split('&')[0]}"
            
            dataTablePage = [
                courseNumber,
                courseName,
                courseCode,
                courseKategori,
                quizName,
                quizDownloadFile
            ]
            print(quizDownloadFile)
            scrapingResult.append(dataTablePage)
            # 4 
            # 7 
            # 12 
            # 27 
            # 32 
            # 35 
            # 42 
            # 42 
            # 69 
            # 70 
            # 82 
            # 85 
            # 87 
            # 98 
            # 103 
            # 114 
            # 169 
            # 179 
            # 194 
            # 198 
            # 222 
            # 223 
            # 254 
            # 257 
            # 266 
            # 268 
            # 275 
            # 281 
            # 286 
            # 302 
            # 314 
            # 315 
            # 326 
            # 327 
            # 334 
            # 340 
            # 355 
            # 376 
            # 379 
            # 381 
            # 387 
            # 388 
            # 404 
            # 429
            # 436
            # 444
            # 447
            # 451
            # 458
            # 481
            # 482
            # 486
            # 490
            # 511
            # 513
            # 521
            # 529
            # 535
            # 537
            # 542
            # 547
            # 548
            # 567
            # 578
            # 595
            # 599
            # 600
            # 623
            # 626
            # 635
            # 650
            # 651
            # 655
            # 659
            # 667
            # 673
            # 686
            # 687
            # 692
            courseExportBtn = driver.find_element(By.XPATH, f"//a[@href='{quizDownloadButton.get("href")}']")
            courseExportBtn.click()

    finally:
        print(f"current index = {dataIndex}")
        df = pd.DataFrame(
            scrapingResult,
            columns=[
                "No",
                "Name Matkul",
                "Kode Matkul",
                "Kategori Matkul",
                "Quiz Name",
                "Quiz File Name",
            ],
        )
        df.to_csv("Matkul-Quiz-Sikola-UH.csv", index=False, header=True, sep=";")

        dfLog = pd.DataFrame(
            [[dataIndex, dataFound, dataNotFound]],
            columns=[
                "Current",
                "Found",
                "NotFound",
            ],
        )

        dfLog.to_csv("log.csv", index=False, header=True, sep=";")
