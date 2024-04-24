import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def extract_emails(text):
    emails = re.findall(r'\S+@\S+', text)
    return emails

def find_email_on_website(website_url):
    paths_to_try = ["", "contact", "contacts", "contactus", "en/contact", "en/contacts", "en/contactus", "/კონტაქტი", "/დაგვიკავშირდით"]

    for path in paths_to_try:
        try_url = website_url + path
        response = requests.get(try_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            mailto_links = soup.find_all('a', href=re.compile(r'mailto:'))

            if mailto_links:
                for link in mailto_links:
                    email_address = link['href'].replace('mailto:', '')
                    return email_address

    return "Couldn't find Email on website."

def find_socials_on_website(website_url):
    paths_to_try = ["", "contact", "contacts", "contactus", "en/contact", "en/contacts", "en/contactus", "/კონტაქტი", "/დაგვიკავშირდით"]

    for path in paths_to_try:
        try_url = website_url + path
        response = requests.get(try_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            all_links = soup.find_all('a')

            if all_links:
                for link in all_links:
                    href = link.get('href')
                    if href and ("facebook" in href or "instagram" in href):
                        return href

    return "Couldn't find Socials on website."

def get_all_emails(loc, bus):
    excel_file = 'database.xlsx'
    df = pd.read_excel(excel_file)
    df_len = df.shape[0]
    found_emails = []
    i = 1
    for index, row in df.iterrows():
        website_url = row['website']
        try:
            response = requests.get(website_url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                mailto_links = soup.find_all('a', href=re.compile(r'mailto:'))

                if mailto_links:
                    link = mailto_links[0]
                    email_address = link['href'].replace('mailto:', '')
                    found_emails.append(email_address)

                else:
                    email = find_email_on_website(website_url)
                    found_emails.append(email)

            else:
                found_emails.append("Couldn't open website.")

        except Exception as e:
            found_emails.append("Error while processing website.")
        print(f"Fetching Emails {i}/{df_len}")
        i+=1

    found_socials = []
    i = 1
    for index, row in df.iterrows():
        website_url = row['website']
        try:
            response = requests.get(website_url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                all_links = soup.find_all('a')
                social_found = False

                if all_links:
                    for link in all_links:
                        href = link.get('href')
                        if href and ("facebook" in href or "instagram" in href):
                            found_socials.append(href)
                            social_found = True
                            break

                if not social_found:
                    found_socials.append(None)

            else:
                found_socials.append("Couldn't open website.")

        except Exception as e:
            found_socials.append("Error while processing website.")
        print(f"Fetching Socials {i}/{df_len}")
        i+=1

    found_emails = [e.strip() for e in found_emails]
    df['email'] = found_emails

    found_socials = [e.strip() if e is not None else e for e in found_socials]
    df['social'] = found_socials

    df.to_excel(f"info/{bus}s in {loc}.xlsx", index=False)

    return_emails = [e for e in found_emails if '@' in e]
    return return_emails

def send_email(email_address, email_password, to_email, subject, html_content, attachment_path, from_):
    from_email = email_address
    msg = MIMEMultipart()
    msg['From'] = f"{from_} <{from_email}>"
    msg['To'] = to_email
    msg['Subject'] = subject

    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)

    if attachment_path != 0 and attachment_path != '0':
        attachment = open(attachment_path + ".pdf", "rb").read()
        attachment_part = MIMEApplication(attachment, Name=attachment_path)
        attachment_part['Content-Disposition'] = f'attachment; filename={attachment_path}'
        msg.attach(attachment_part)

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()

    server.login(email_address, email_password)

    server.sendmail(from_email, to_email, msg.as_string())

    server.quit()