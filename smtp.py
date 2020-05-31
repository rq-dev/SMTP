import socket
import ssl
from base64 import b64encode
from configparser import ConfigParser

#
# # SMTP
# Made by Roman Yaschenko MO-202#
# How to use?
# 1) Open config.txt;
# 2) Fill in: Login, Password, Addressee has to be separated by " ", Theme,
# Attachments has to be separated by ",", Text, Host and Port.
# 3)Run: smtp.py. See result on pic 2.


def send_message(address, port, login, password, addressee, message):
    with_dot = message + "\n."
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock = ssl.wrap_socket(sock)
        sock.settimeout(1)
        sock.connect((address, port))
        send_command(sock, b'EHLO test')
        send_command(sock, b'AUTH LOGIN')
        send_command(sock, b64encode(login.encode()))
        send_command(sock, b64encode(password.encode()))
        send_command(sock, b'MAIL FROM: ' + login.encode())
        send_command(sock, b'RCPT TO: ' + addressee.encode())
        send_command(sock, b'DATA')
        send_command(sock, with_dot.encode())
        print('### Message has been sent to ' + addressee + ' !')


def create_message(login, addressee, theme, text, attachments):
    return (
        f'From: {login}\n'
        f'To: {addressee}\n'
        f'Subject: {theme}\n'
        'MIME-Version: 1.0\n'
        f'Content-Type: multipart/mixed; boundary="{"___"}"\n\n'
        f'--{"___"}\n'
        'Content-Type: text/plain; charset=utf-8\n'
        'Content-Transfer-Encoding: 8bit\n\n'
        f'{text}\n'
        f'--{"___"}\n'
        f'{attachments}--\n.'
    )


def prepare_attachments(attachments):
    message_attachments = ''
    files = attachments.split(', ')
    for file in files:
        (_, extension) = file.split('.')
        with open(file, 'rb') as f:
            file_encoded = b64encode(f.read())
            message_attachments += \
                (f'Content-Disposition: attachment; '
                 f'filename="{file}"\n'
                 f'Content-Transfer-Encoding: base64\n'
                 f'Content-Type: name="{file}"\n\n') \
                + file_encoded.decode() + \
                f'\n--{"___"}\n'
    return message_attachments


def send_command(sock, command, buffer=1024):
    sock.send(command + b'\n')
    return sock.recv(buffer).decode()


def parse_config(config_parser):
    message = config_parser['Message']
    sender = config_parser['Sender']
    recipients = [' '.join(config_parser['Addressee'])]
    login = sender['Login']
    password = sender['Password']
    theme = message['Theme']
    text = message['Text']
    attachment_files = message['Attachments']
    return message, sender, recipients, login, theme, text, attachment_files, password


def main():
    config_parser = ConfigParser(allow_no_value=True)
    with open('config.txt', 'r') as f:
        config_parser.read_file(f)
    (message, sender, recipients, login, theme, text, attachment_files, password) = parse_config(config_parser)
    attachments = prepare_attachments(attachment_files)
    server_info = config_parser['Server']
    (address, port) =(server_info['Host']), int(server_info['Port'])
    str_addressees = ""
    for addressee in recipients:
        str_addressees += addressee

    array_addressees = str_addressees.split(" ")
    for addressee in array_addressees:
        generated_message = create_message(login, addressee, theme, text, attachments)
        send_message(address, port, login, password, addressee, generated_message)


if __name__ == '__main__':
    main()