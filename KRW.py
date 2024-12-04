from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

service = Service(os.getenv("CHROME_DRIVER_PATH"))
options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(service=service, options=options)

THRESHOLD_RATE = 1430


def check_exchange_rate():
    print("Getting exchange rate...")
    driver.get(os.getenv("URL"))
    time.sleep(5)  # Give the page time to load dynamically loaded content

    soup = BeautifulSoup(driver.page_source, "html.parser")
    exchange_rate = soup.find_all("div", class_="YMlKec fxKbKc")
    if not exchange_rate:
        print("Failed to get exchange rate, trying again...")
        return check_exchange_rate()

    return exchange_rate[0].text


def send_email(subject, body):
    sender_email = os.getenv("EMAIL_ADDRESS")
    receiver_email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, [sender_email, receiver_email], text)
        server.quit()
        print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")


def main():
    try:
        interval = 300  # 5 minutes
        while True:
            current_rate = check_exchange_rate()
            if not current_rate:
                break
            current_rate = current_rate.replace(",", "")
            if float(current_rate) > THRESHOLD_RATE:
                subject = "💸 EZ MONEY 💸"
                body = "The current rate is " + str(current_rate) + " — get that bag 🤑"
                send_email(subject, body)
            else:
                print(
                    "The current rate is "
                    + str(current_rate)
                    + " — not high enough yet 😔"
                )
            time.sleep(interval)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
