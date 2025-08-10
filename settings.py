from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
import re
import threading
import time
import csv
import requests
import pandas as pd

current_year = datetime.now().year
current_date = datetime.now()
new_formatted_date = current_date.strftime("%y-%m-%d")
name_present_day = datetime.now().strftime("%y-%m-%d")
headless_options = (
    webdriver.ChromeOptions()
)  # Set up Selenium WebDriver with headless Chrome
headless_options.add_argument("--headless")  # Run Chrome in headless mode
headless_options.add_argument("--disable-gpu")  # Disable GPU acceleration
headless_options.add_argument("--no-sandbox")  # Bypass OS security model
headless_options.add_argument(
    "--disable-dev-shm-usage"
)  # Overcome limited resource problems
headless_options.add_argument(
    "--window-size=1920,1080"
)  # Set window size for headless mode
#
headless_options.add_argument(
    "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.0 Safari/537.36"
)
#
head_options = (
    webdriver.ChromeOptions()
)  # Set up Selenium WebDriver with headless Chrome
head_options.add_argument("--disable-gpu")  # Disable GPU acceleration
head_options.add_argument("--no-sandbox")  # Bypass OS security model
head_options.add_argument(
    "--disable-dev-shm-usage"
)  # Overcome limited resource problems
head_options.add_argument(
    "--window-size=1920,1080"
)  # Set window size for headless mode
#
head_options.add_argument(
    "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.0 Safari/537.36"
)
#
