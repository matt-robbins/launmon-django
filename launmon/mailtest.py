import smtplib, ssl

smtp_server = "smtp.porkbun.com"
port = 587  # For starttls
sender_email = "admin@spintracker.app"
receiver_email = "matthew.robbins@gmail.com"
password = "Gu1t4rS0ld3r!"

# Create a secure SSL context
context = ssl.create_default_context()

message = """\
Subject: Hi there

This message is sent from Python."""

# Try to log in to server and send email
try:
    server = smtplib.SMTP(smtp_server,port)
    server.ehlo() # Can be omitted
    server.starttls(context=context) # Secure the connection
    server.ehlo() # Can be omitted
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
    # TODO: Send email here
except Exception as e:
    # Print any error messages to stdout
    print(e)
finally:
    server.quit() 


