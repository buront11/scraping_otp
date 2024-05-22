import time
import os
import json
import re
import requests
import subprocess
import oathtool

from dotenv import load_dotenv

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service

def get_one_time_password():
    # two_step_authentication = ['oathtool', '--totp', '--base32', '4UI5UKOBOK7NATGHAHRGLRU3N5AIXTAU']
    # return str(subprocess.check_output(two_step_authentication).decode('utf-8'))
    return str(oathtool.generate_otp('4UI5UKOBOK7NATGHAHRGLRU3N5AIXTAU'))

def get_paloalto_otp(driver, serial_number):
    # 親要素じゃないとclickできなかったので親を指定
    # driver.find_element(By.XPATH, "//span[text()='Products']/..").click()

    # driver.find_element(By.XPATH, "//a[contains(., 'Device Certificates')]").click()

    # driver.find_element(By.XPATH, "//a[contains(@href, 'GenerateOneTimePassword')]").click()

    # directでOTP Generate pageのURLを指定してしまって良い、環境変数にCSPアカウントのシリアルを入れて、それを参照してURLを踏む
    driver.get("https://support.paloaltonetworks.com/SupportAccount/GenerateOneTimePassword/255359")

    # ここでPanOSのradio buttonをclickする処理を入れる、今は初期値なので一旦省略

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # ここでのシリアル番号はstgのb4a49bのものを選択
    serial_number_input = driver.find_element(By.ID, "SerialNumber")
    serial_number_input.send_keys(serial_number)

    time.sleep(3)

    serial_number_input.send_keys(Keys.ENTER)

    time.sleep(1)

    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    OTP = driver.find_element(By.XPATH, "//dt[text()='Password:']/following-sibling::dd").text

    return OTP

def get_paloalto_pin(driver, serial_number):
    pass

def main(serial_number):
    try:
        load_dotenv()

        options = webdriver.ChromeOptions()

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--headless")


        chrome_service = webdriver.chrome.service.Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=chrome_service, options=options)

        # driver = webdriver.Remote(
        #     command_executor='http://selenium:4444/wd/hub',
        #     options=options
        # )

        driver.implicitly_wait(10)

        driver.get(f"https://sso.paloaltonetworks.com/")
        driver.maximize_window()

        email = driver.find_element(By.ID, "idp-discovery-username")
        email.send_keys(os.environ["EMAIL"])

        driver.find_element(By.ID, "idp-discovery-submit").click()

        passwd = driver.find_element(By.ID, "okta-signin-password")
        passwd.send_keys(os.environ["PASSWD"])

        driver.find_element(By.ID, "okta-signin-submit").click()

        otp = driver.find_element(By.NAME, "answer")
        otp.send_keys(get_one_time_password())

        ## 上が理想だが現状2つ要素が見つかるのでうまくclickできない
        # driver.find_element(By.XPATH, "//input[contains(@type, 'submit') and contains(@class, 'button-primary')]").click()
        driver.find_element(By.XPATH, "//input[contains(@value,'確認') or contains(@value, 'Verify')]").click()

        time.sleep(3)

        csp_url = driver.find_element(By.XPATH, "//a[contains(@aria-label, 'Customer Support Portal')]").get_attribute("href")
        print(csp_url)

        driver.get(csp_url)

        time.sleep(5)

        otp = get_paloalto_otp(driver, serial_number)

        return otp
    finally:
        driver.quit()


if __name__=='__main__':
    import argparse

    serial_number = "007054000251473"

    ## 現状の問題　OTPでログインしてから素早くもう一度ログインしようとするとOTPでログインできるのは一度だけなので弾かれる

    ## serial_numberはshow system infoから取得可能
    main(serial_number)
    # get_one_time_password()
    # get_palo_api_key()
