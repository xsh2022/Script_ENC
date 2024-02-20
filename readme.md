# EMail-NGROK 联动脚本（EMail-NGROK Co-op Script）

摘要：实现了开启NGROK并通过电子邮件获取NGROK地址的功能，省去了出门在外忘记了 NGROK 地址的烦恼。

Abstract: This script allow you to start NGROK while using an email to get NGROK address, which stops you from forgetting NGROK address when you are out of home.

## 实现原理（Realizing）

### 中文

* 电子邮件收发依靠 imaplib 库和 smtplib 库
* NGROK实现依靠 pyngrok 库

### English

* The email part uses imaplib and smtplib
* The NGROK part uses pyngrok library

## 使用方法（Usage）：

### 中文

1. 使用pip安装 pyngrok 库，注册NGROK，获取TOKEN，此外你需要注册一个邮箱（最好是163）、开启其SMTP和IMAP功能，记住口令。
2. 第一次使用时直接打开，会在脚本的目录下创建config.json文件。
3. 修改config.json文件中的选项，他们的命名很直观，如果你会英文那么一看就懂。不懂参照附录2
4. 再次运行，如果没有任何异常，说明运行成功。
5. 向指定的邮箱发送邮件，内容任意，主题为“get ngrok”，等待一会儿，就会收到主题为“Command operated”的邮件，内容为NGROK的地址和端口

### English

1. Install the pyngrok library using pip, register for NGROK, and obtain a TOKEN. Additionally, you need to register an email address (preferably with 163.com), enable its SMTP and IMAP functions, and remember the password.
2. When using it for the first time, simply open it, and it will create a config.json file in the script's directory.
3. Modify the options in the config.json file; their names are intuitive, so if you understand English, you will grasp them at a glance. If not, refer to Appendix 2.
4. Run it again; if there are no exceptions, it indicates a successful run.
5. Send an email to the specified email address with any content, the subject should be "get ngrok". Wait for a while, and you will receive an email with the subject "Command operated" containing the address and port of NGROK.

# 附录（Appendix）

## 附录1. PIP安装PyNGROK库（Appendix 1. Install PyNGROK using PIP）

### 中文

打开Windows命令行或Linux、Mac-OS终端，输入：

```bash
python -m pip install pyngrok
```

### English

Open cmdline of windows or terminal of linux or Mac-OS, enter:

```bash
python -m pip install pyngrok
```

## 附录2. “config.json”的参数说明（Appendix 2. Descriptions of 'config.json'）：

### 中文

以如下config.json文件为示例：

```json
{
  "ngrok": {
    "ngrok_token": "1111111111111111111111111111111111111111111111111",
    "conn_type": "tcp",
    "conn_port": 22
  },
  "email": {
    "imap":{
      "host": "imap.163.com",
      "port": 993,
      "username": "example@163.com",
      "password": "ABCDEFGHIJKLMNOP"
    },
    "smtp":{
      "host": "smtp.163.com",
      "port": 465,
      "username": "example@163.com",
      "password": "ABCDEFGHIJKLMNOP"
    }
  }
}
```

| 参数             | 说明                                                           |
|----------------|--------------------------------------------------------------|
| ngrok_token    | NGROK的TOKEN码，在官网查询                                           |
| conn_type      | NGROK映射的类型，可以选择TCP、HTTP等，具体参考NGROK官网。``例如你可以选择TCP来访问ssh端口22。 |
| conn_port      | NGROK映射的端口。                                                  |
| region         | NGROK地区，可选择日本（jp）、亚洲（ap）、美国（us）、欧洲（eu）、澳大利亚（au）              |
| imap->host     | IMAP的主机地址。                                                   |
| imap->port     | IMAP的端口，目前只支持SSL的端口                                          |
| imap->username | IMAP用户名，一般与邮箱同名                                              |
| imap->password | IMAP密码，163设置页面中的“授权码”，一般与网页邮箱的登录密码不同                         |
| smtp->xxx      | 与imap->xxx类似                                                 |

### English

Take the following config.json for example:

```json
{
  "ngrok": {
    "ngrok_token": "1111111111111111111111111111111111111111111111111",
    "conn_type": "tcp",
    "conn_port": 22
  },
  "email": {
    "imap":{
      "host": "imap.163.com",
      "port": 993,
      "username": "example@163.com",
      "password": "ABCDEFGHIJKLMNOP"
    },
    "smtp":{
      "host": "smtp.163.com",
      "port": 465,
      "username": "example@163.com",
      "password": "ABCDEFGHIJKLMNOP"
    }
  }
}
```

| Parameter      | Description                                                                                                                                                          |
|----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ngrok_token    | Token code for NGROK, check on the official website                                                                                                                  |
| conn_type      | Type of mapping for NGROK, options include TCP, HTTP, etc., refer to the NGROK official website for details.``For example, you can choose TCP to access ssh port 22. |
| conn_port      | Port for NGROK mapping                                                                                                                                               |
| region         | NGROK region, Japan (jp), Asia (ap), United States (us), Europe (eu) and Australia (au) are selections                                                               |
| imap->host     | Host address for IMAP                                                                                                                                                |
| imap->port     | Port for IMAP, currently only supports SSL port                                                                                                                      |
| imap->username | IMAP username, usually the same as the email address                                                                                                                 |
| imap->password | IMAP password, "authorization code" on the 163 settings page, usually different from the login password for webmail                                                  |
| smtp->xxx      | Similar to imap->xxxW                                                                                                                                                |
