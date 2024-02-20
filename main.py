#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import imaplib
import json
import os
import signal
import smtplib
import time
import email
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from imaplib import IMAP4_SSL
from pyngrok import ngrok


stop_signal = False


DEFAULT_CONFIG_CONTENT = \
    '''{
  "ngrok": {
    "ngrok_token": "1234567890",
    "conn_type": "tcp",
    "conn_port": 22
  },
  "email": {
    "imap":{
      "host": "imap.example.com",
      "port": 993,
      "username": "user@mail.example.com",
      "password": "123456"
    },
    "smtp":{
      "host": "smtp.example.com",
      "port": 465,
      "username": "user@mail.example.com",
      "password": "123456"
    }
  }
}
'''
ALLOWED_NGROK_CONN_TYPES = ['tcp', 'http']


def read_config(path):
    try:
        f = open(path, 'r')
    except FileNotFoundError:
        print('File not found!')
        return 1, None
    except Exception as e:
        print(f'Unexpected error:{e}')
        return -1, None
    else:
        pass

    try:
        config_str = f.read()
        f.close()
        config_obj = json.loads(config_str)

    except Exception as e:
        print(f'Unexpected error:{e}')
        return -1, '', ''
    else:
        pass
    return 0, config_obj


def create_config_file(path):
    d, f = os.path.split(path)
    if not os.path.isdir(d):
        try:
            os.makedirs(d)
        except PermissionError:
            print(f'Got no permission to create dir:[{d}]')
            return 1
        except Exception as e:
            print(f'Unexpected error:{e}')
            return -1
        else:
            pass
    try:
        f = open(path, 'w')
        f.write(DEFAULT_CONFIG_CONTENT)
        f.close()
    except PermissionError:
        print(f'Got no permission to write:[{path}]')
        return 1
    except Exception as e:
        print(f'Unexpected error:{e}')
        return -1
    return 0


def stop_handler(signum, _):
    global stop_signal
    print(f'----\nSignum: [{signum}]\n----')
    stop_signal = True


def main():

    # 准备变量
    signal.signal(signal.SIGINT, stop_handler)
    root_dir = os.path.split(os.path.realpath(__file__))[0]
    config_path = os.path.join(root_dir, 'config.json')

    # 读取配置
    ret, config = read_config(config_path)
    if ret == -1:
        return -1
    elif ret == 1:
        ret = create_config_file(config_path)
        if ret != 0:
            return ret
        else:
            print('Created template config file! Please fill it and restart the script.')
            return 0
    else:
        pass
    ngrok_conn_type = config['ngrok']['conn_type']
    ngrok_conn_port = config['ngrok']['conn_port']
    ngrok_token = config['ngrok']['ngrok_token']

    imap_host = config['email']['imap']['host']
    imap_port = config['email']['imap']['port']
    imap_username = config['email']['imap']['username']
    imap_password = config['email']['imap']['password']

    smtp_host = config['email']['smtp']['host']
    smtp_port = config['email']['smtp']['port']
    smtp_username = config['email']['smtp']['username']
    smtp_password = config['email']['smtp']['password']

    if ngrok_conn_type not in ALLOWED_NGROK_CONN_TYPES:
        print(f'[{ngrok_conn_type}] is not an allowed ngrok conn type')
        return 2

    # 设置ngrok连接
    ngrok.set_auth_token(ngrok_token)

    # IMAP 初始化
    try:
        imaplib.Commands['ID'] = ('AUTH',)
        imap_conn: IMAP4_SSL = imaplib.IMAP4_SSL(host=imap_host, port=imap_port)
    except Exception as e:
        print(f'Unexpected error: [{e}]')
        return -1
    else:
        pass
    # IMAP连接
    while True:
        try:
            imap_conn.login(imap_username, imap_password)
            # 添加ID命令
            ag = ("name", "automail_xsh", "contact", "automail_xsh@163.com", "version", "1.0.0",
                    "vendor", "myclient")
            stat, dat = imap_conn._simple_command('ID', '("' + '" "'.join(ag) + '")')
        except imaplib.IMAP4_SSL.error as e:
            print(f'IMAP login failure! Retrying in 5 seconds. Error:{e}')
            time.sleep(5)
            continue
        except Exception as e:
            print(f'Unexpected error: [{e}]')
            return 1
        else:
            break

    # NGROK连接
    ngrok_conn = ngrok.connect(ngrok_conn_port, ngrok_conn_type)
    print(f'Config is read and ready to work!\n')

    # 主循环
    while True:

        # 检查NGROK
        try:
            ngrok.get_tunnels()
        except Exception as e:
            if stop_signal:
                ngrok.disconnect(ngrok_conn.public_url)
                break
            else:
                print(f'Unexpected error: [{e}], restarting ngrok conn....')
                ngrok_conn = ngrok.connect(ngrok_conn_port, ngrok_conn_type)
        else:
            if stop_signal:
                ngrok.disconnect(ngrok_conn.public_url)
                break

        # IMAP读取
        stat, data = imap_conn.select('INBOX')
        while stat != 'OK':
            stat, data = imap_conn.select('INBOX')
        stat, data = imap_conn.search(None, 'UNSEEN')
        if stat != 'OK':
            print('Failure when reading mail')
            time.sleep(5)
            continue
        email_ids = data[0].split()
        mail_cnt = len(email_ids)
        unseen_msg_list = []

        for i in range(mail_cnt-1, -1, -1):
            imap_conn.store(email_ids[i], '+FLAGS', '\\Seen')
            mail_stat, mail_data = imap_conn.fetch(email_ids[i], '(RFC822)')
            msg = email.message_from_bytes(mail_data[0][1])
            subject_obj = email.header.decode_header(msg.get('subject'))
            default_code = subject_obj[0][1]
            subject_str = subject_obj[0][0]
            if default_code is not None:
                subject_str = subject_str.decode(default_code)
            content_list = []
            if msg.is_multipart():
                pl = msg.get_payload()
                for single_mail in pl:
                    ctype = single_mail.get_content_type()
                    if 'html' in ctype:
                        html = str(single_mail.get_payload(decode=True), single_mail.get('content-type').split('=')[1])
                    else:
                        txt = msg.get_payload(decode=True)
                        html = str(txt, default_code) if txt else ''
                    content_list.append(html)
            else:
                txt = msg.get_payload(decode=True)
                html = str(txt, default_code) if txt else ''
                content_list.append(html)
            sender: str = msg.get('from')
            t = sender.find('<')
            sender = sender[t+1:len(sender)-1:1]
            unseen_msg_list.append([subject_str, sender, content_list])
        # 处理读取的邮件、发送回复
        for [subject, sender, body] in unseen_msg_list:
            if subject.lower() == 'get ngrok':
                subject_back = 'Command operated'
                sender_back = smtp_username
                receiver_back = sender
                body_back = (f'URL: {ngrok_conn.public_url}\n'
                             f'Port: {ngrok_conn_port}\n')
            else:
                subject_back = 'Mail received'
                sender_back = smtp_username
                receiver_back = sender
                body_back = 'We are trying to reply you ASAP'
            msg = MIMEMultipart()
            msg['from'] = formataddr((Header('Auto Mail', 'utf-8').encode(), sender_back))
            msg['to'] = receiver_back
            msg['subject'] = Header(subject_back, 'utf-8').encode()
            msg.attach(MIMEText(body_back, 'plain', 'utf-8'))
            # SMTP连接
            try:
                smtp_conn = smtplib.SMTP_SSL(smtp_host, smtp_port)
                smtp_conn.login(smtp_username, smtp_password)
                smtp_conn.ehlo_or_helo_if_needed()
                smtp_conn.sendmail(sender_back, receiver_back, msg.as_string())
            except Exception as e:
                print(f'Unexpected error: [{e}]')
            else:
                print(f'===================================\n'
                      f'     M A I L    H A N D L E D      \n'
                      f'-----------------------------------\n'
                      f'Subject: [{subject}]\n'
                      f'From: [{sender}]\n'
                      f'-----------------------------------\n'
                      f'                BACK               \n'
                      f'-----------------------------------\n'
                      f'Subject: [{subject_back}]\n'
                      f'Content:\n'
                      f'- - - - - - - - - - - - - - - - - -\n'
                      f'{body_back}\n'
                      f'===================================\n')
        time.sleep(1)
    imap_conn.close()
    return 0


if __name__ == '__main__':
    main_ret = main()
    exit(main_ret)
