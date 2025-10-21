import email.message 
msg=email.message.EmailMessage()
msg["From"]="Ethanlin921116@gmail.com"
msg["To"]="linnorman0628@gmail.com"
msg["Subject"]="🖕🏿🖕🏿🖕🏿🖕🏿🖕🏿🖕🏿"
msg.set_content("操")
import smtplib
server=smtplib.SMTP_SSL("smtp.gmail.com", 465)
server.login("Ethanlin921116@gmail.com", "pmxy vghp qngk cxcg")
for i in range (5):
    server.send_message(msg)
server.close()
#linnorman0628@gmail.com