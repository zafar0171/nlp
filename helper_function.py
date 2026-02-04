from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from datetime import datetime
from email.message import EmailMessage

def send_email(subject, messageBody, destination, msgType):

    today = datetime.now()
    todayDate = today.strftime("%d %B, %Y")

    email_subject = subject + ' (Dated:' +  todayDate +')'
    sender_email_address = creds.emailId
    receivers_email_address = destination

    email_smtp = creds.smtpGateway
    email_password = creds.emailPw

    message = EmailMessage() 
    message['Subject'] = email_subject 
    message['From'] = sender_email_address
    # The message needs to have a To: header
    # - putting yourself is an old convention
    message['To'] = creds.emailId
    message['Cc'] = ",".join(receivers_email_address)
    # message['Bcc'] = ",".join(receivers_email_address)

    # with open('message.html', 'r') as file:
    # file_content = file.read()
    message.set_content(messageBody, subtype=msgType)

    with smtplib.SMTP(email_smtp, '587') as server:
        server.ehlo() 
        server.starttls() 
        server.login(sender_email_address, email_password) 
        server.send_message(message) 
        server.quit()



def send_email_new(subject, messageBody, destination, msgType):
    try:
        # Get current date
        today = datetime.now()
        todayDate = today.strftime("%d %B, %Y")

        # Create message container
        msg = MIMEMultipart()
        msg['Subject'] = f"{subject} (Dated: {todayDate})"
        msg['From'] = creds.emailId

        # Attach the message body
        body = MIMEText(messageBody, msgType)
        msg.attach(body)

        # Ensure destination is a list
        if not isinstance(destination, list):
            destination = [destination]

        print(f"Sending email: Subject: {subject} (Dated: {todayDate})")

        # Setup the SMTP server
        server = smtplib.SMTP(creds.smtpGateway, creds.smtpPort)
        server.ehlo()
        server.starttls()
        server.login(creds.emailId, creds.emailPw)

        # Send the email to each recipient
        for dest in destination:
            try:
                msg['To'] = dest
                server.sendmail(creds.emailId, dest, msg.as_string())
                print(f"Email sent successfully to {dest}")
            except Exception as e:
                print(f"Failed to send email to {dest}. Error: {str(e)}")

        # Quit the server
        server.quit()

    except Exception as e:
        print(f"An error occurred: {str(e)}")