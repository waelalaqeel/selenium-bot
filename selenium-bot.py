# selenium-bot.py

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO

# إعدادات التوكن والتليجرام
TELEGRAM_BOT_TOKEN = "7884802024:AAH1nRQuWQMSbUyNTuoLb9F3VmdQwd5TdXE"
TELEGRAM_CHAT_ID = "782991787"

# إعداد المتصفح
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
service = Service()
driver = webdriver.Chrome(service=service, options=options)

# تحميل بيانات العقود
df = pd.read_csv("contracts.csv")

# مراقبة العقود كل دقيقة
while True:
    for index, row in df.iterrows():
        contract = row['contract']
        url = row['url']
        target_price = float(row['target_price'])

        try:
            driver.get(url)
            time.sleep(5)
            price_element = driver.find_element(By.XPATH, "//div[contains(@class, 'price')]")
            price_text = price_element.text.strip().replace('$', '')
            price = float(price_text)

            if price >= target_price:
                screenshot = driver.get_screenshot_as_png()
                image = Image.open(BytesIO(screenshot))

                # حفظ الصورة
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = f"screenshot_{contract}_{timestamp}.png"
                image.save(image_path)

                # إرسال الصورة للتليجرام
                with open(image_path, 'rb') as photo:
                    requests.post(
                        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto",
                        data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"🎯 {contract} hit {price:.2f}"},
                        files={"photo": photo}
                    )
        except Exception as e:
            print(f"[{contract}] Error: {e}")

    print("⏱️ Waiting for next round...")
    time.sleep(60)
