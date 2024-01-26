from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv("SIKOLA_USERNAME")
PASSWORD = os.getenv("SIKOLA_PASSWORD")

try:
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get("https://sikola.unhas.ac.id/")

    eLoginUsername = driver.find_element(By.ID, "login")
    eLoginUsername.clear()
    eLoginUsername.send_keys(USERNAME)
    eLoginPassword = driver.find_element(By.ID, "password")
    eLoginPassword.clear()
    eLoginPassword.send_keys(PASSWORD)

    eLoginButton = driver.find_element(By.XPATH, "//button[@name='submitAuth']")
    eLoginButton.click()

    eMasterMatakuliahButtonItem = WebDriverWait(driver, 25).until(
        EC.presence_of_element_located(
            (By.XPATH, "//a[contains(text(), 'Daftar Master Mata Kuliah')]")
        )
    )

    eMasterMatakuliahButton = driver.find_element(
        By.XPATH, "//a[contains(text(), 'Daftar Master Mata Kuliah')]"
    )
    eMasterMatakuliahButton.click()

    currentPage = 1
    scrapingResult = []
    for page in range(622):
        eMasterMatakuliahButtonItem = WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.XPATH, "//table[@id='course-list']"))
        )

        eTableListMatakuliah = driver.find_element(
            By.XPATH, "//table[@id='course-list']"
        ).get_attribute("innerHTML")

        tableBodyParser = BeautifulSoup(eTableListMatakuliah, "html.parser")
        listItemTable = tableBodyParser.find_all("tr")

        for itemIndex in range(1, len(listItemTable)):
            item = listItemTable[itemIndex].find_all("td")
            courseLink = item[1].find("a").get("href")
            courseName = item[1].find("a").text
            courseCode = item[2].text
            courseCategory = item[4].text

            dataTablePage = [
                (currentPage - 1) * 20 + itemIndex,
                courseLink,
                courseName,
                courseCode,
                courseCategory,
            ]
            scrapingResult.append(dataTablePage)

        # Export Data Scraping Result
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

        df.to_csv("Scraping-Matkul-Sikola-UH.csv", index=False, header=True, sep=";")

        eMasterMatakuliahTableNextBtn = driver.find_element(
            By.XPATH, "//a[@title='next page']"
        )
        eMasterMatakuliahTableNextBtn.click()
        currentPage += 1


finally:
    driver.quit()
