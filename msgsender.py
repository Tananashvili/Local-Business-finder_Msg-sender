import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

email_address = "zaza.tana@gmail.com"
email_password = "niij gmqm fhki pvgl"

subject = "სარეკლამო რგოლი 50 დოლარად"
from_email = email_address
to_email = "saba.tananashvili@gmail.com"
with open("offer.html", "r", encoding='utf-8') as html_file:
        html_content = html_file.read()

msg = MIMEMultipart()
msg['From'] = f"Zaza Tananashvili <{from_email}>"
msg['To'] = to_email
msg['Subject'] = subject

html_part = MIMEText(html_content, 'html')
msg.attach(html_part)

file_path = "Singing Wine Bottles.pdf"  # Replace with the path to your file
attachment = open(file_path, "rb").read()
attachment_part = MIMEApplication(attachment, Name=file_path)
attachment_part['Content-Disposition'] = f'attachment; filename={file_path}'
msg.attach(attachment_part)

smtp_server = "smtp.gmail.com"
smtp_port = 587

server = smtplib.SMTP(smtp_server, smtp_port)
server.starttls()

server.login(email_address, email_password)

server.sendmail(from_email, to_email, msg.as_string())

server.quit()

def send_email(email_address, email_password, to_email, subject, html_content):
    from_email = email_address
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()

    server.login(email_address, email_password)

    server.sendmail(from_email, to_email, msg.as_string())

    server.quit()