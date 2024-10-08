import argparse
import csv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
import ssl
import html2text

"""
python3 sendmail.py -c users.csv -t mail.template -e "no-reply@cesnet.dev" -r "cloud@metacentrum.cz" -s "rs.cesnet.dev" -p 465
"""


def connect(host: str, port: int, login: str = "", password: str = "", encryption_method: str = "TLS"):
    """
    Opens connection to specified server with parameters. If some error occurred, returns None
    Possible values for encryption_method: SSL, TLS, STARTTLS, ANY
    Possible errors:
     - host (with port) is not correct
     - server does not support encryption method provided (on selected port)
     - timeout
     - login or password is not correct
    """
    print(4, f"mail.connect(host={host},port={port},login={login},encryption={encryption_method})")
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    try:

        if encryption_method in ("SSL", "TLS"):
            # explicit mode requested, server must support SSL or TLS
            # https://docs.python.org/3/library/smtplib.html#smtplib.SMTP_SSL
            smtp_connection = smtplib.SMTP_SSL(host=host, port=port, context=context)
        else:
            # implicit mode requested, communication starts unencrypted,
            # later, if server supports (starttls) can be upgraded
            # https://docs.python.org/3/library/smtplib.html#smtplib.SMTP
            smtp_connection = smtplib.SMTP(host=host, port=port)

    except smtplib.SMTPConnectError as e:
        print(2, f"Could not connect to SMTP server {host}:{port}. Hostname or port is wrong. Error text: {e}")
        return None
    except TimeoutError as e:
        print(2, f"Could not connect to SMTP server {host}{port}. Time is up. Error text: {e}")
        return None
    except Exception as e:
        print(2, f"Could not connect to SMTP server {host}{port}. Undefined error. Error text: {e}")
        return None

    if encryption_method == "STARTTLS":
        # implicit method, negotiating encryption
        smtp_connection.starttls(context=context)

    # https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.ehlo_or_helo_if_needed
    try:
        smtp_connection.ehlo_or_helo_if_needed()
    except smtplib.SMTPHeloError as e:
        print(2, f"We could not understand HELO/EHLO from {host}:{port}. Error text: {e}")
        smtp_connection.quit()
        return None
    except Exception as e:
        print(2, f"Undefined error when sending HELO/EHLO from {host}:{port}. Error text: {e}")
        smtp_connection.quit()
        return None

    # https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.login
    # SMTP must authenticate and authorize me
    try:
        if login and password:
            smtp_connection.login(login, password)
    except smtplib.SMTPAuthenticationError as e:
        print(2, f"Username and password are not accepted by {host}:{port}. Error text: {e}")
        smtp_connection.quit()
        return None
    except smtplib.SMTPNotSupportedError as e:
        print(2, f"Server {host}:{port} does not accept authentication. Error text: {e}")
        smtp_connection.quit()
        return None
    except smtplib.SMTPException as e:
        print(2, f"Server {host}:{port} uses some weird authentication method. Error text: {e}")
        smtp_connection.quit()
        return None
    except Exception as e:
        print(2, f"Undefined error when authenticating to {host}:{port}. Error text: {e}")
        smtp_connection.quit()
        return None

    return smtp_connection


def convert_html_to_text(html_input: str):
    """
    Converts HTML to plaintext using html2text with a reasonable setup.
    :param html_input: HTML source
    :return: Plaintext version of the input
    """
    handler = html2text.HTML2Text()
    handler.inline_links = False
    handler.body_width = None
    handler.ignore_emphasis = True
    handler.ignore_images = True
    handler.ignore_tables = True
    handler.protect_links = True
    handler.ignore_mailto_links = True
    return handler.handle(html_input)


#
# Parse command-line arguments
parser = argparse.ArgumentParser(description='Send emails from CSV with Jinja2 template')
parser.add_argument('-c', '--csv', help='Path to CSV file containing email addresses and names')
parser.add_argument('-t', '--template', help='Name of the Jinja2 template located in the folder - there should be two files: template.txt and template.html')
parser.add_argument('--html2text', action='store_true', help='Generate plaintext mail part from HTML template. The *.txt template file will be ignored. Off by default.')
parser.add_argument('-e', '--email', help='Sender email address')
parser.add_argument('-r', '--reply', help='Reply-to email address')
parser.add_argument('--recipients', help='Comma-delimited email addresses to send the mail to instead (keeps "To:" and "Cc:" headers unchanged)')
parser.add_argument('-S', '--subject', help='Email subject')
parser.add_argument('--subject_prefix', help='Email subject prefix (will be prepended to --subject)')
parser.add_argument('-s', '--smtp_server', help='SMTP server address')
parser.add_argument('-p', '--smtp_port', help='SMTP server port', type=int, default=25)
parser.add_argument('-u', '--username', help='SMTP server username')
parser.add_argument('-w', '--password', help='SMTP server password')
parser.add_argument('--sendemail', action='store_true' ,help='Send email, by default it only generates email content and prints it.')

args = parser.parse_args()
# Read email template
has_html_template = False
has_txt_template = False

if not args.template:
    print("Please provide a template file")
    exit(1)
if not args.subject:
    print("Please provide a subject template string")
    exit(1)
# TODO: zamyslet se jestli pri trigerovani vytvaret novy csv file? Nebo pridat moznost arraye.
if args.csv is None:
    print("Please provide a CSV file")
    exit(1)

# Determine if the template is HTML or plain text
if os.path.isfile(args.template+".html"):
    with open(args.template+".html", 'r') as html_template_file:
        html_template_content = html_template_file.read()
    has_html_template = True
if has_html_template and args.html2text:
    template_content = convert_html_to_text(html_template_content)
    has_txt_template = True
elif os.path.isfile(args.template+".txt"):
    with open(args.template+".txt", 'r') as template_file:
        template_content = template_file.read()
    has_txt_template = True
elif os.path.isfile(args.template+".tmpl"):
    with open(args.template+".tmpl", 'r') as template_file:
        template_content = template_file.read()
    has_txt_template = True

# Prepare subject templates
subject_template = Template(args.subject)
if args.subject_prefix:
    subject_prefix_template = Template(args.subject_prefix)

# Prepare body templates
print(os.path.isfile(args.template+".txt"), os.path)
if 'template_content' in locals():
    email_template = Template(template_content)
if 'html_template_content' in locals():
    html_email_template = Template(html_template_content)

EMAIL_ADDRESS_DELIMITER = ','

# Open CSV file and send emails
with open(args.csv, 'r') as file:
    reader = csv.DictReader(file, delimiter=';')
    for row in reader:
        csv_files=[]
        for key, value in row.items():
            if '.csv' in value:
                csv_files.append(value)
        csv_content_dict = {}
        if csv_files:
            for csv_file in csv_files:
                name_without_extension = os.path.splitext(csv_file)[0]
                try:
                    with open(csv_file, newline='') as f:
                        reader = csv.DictReader(f, delimiter=';')
                        csv_content_dict[name_without_extension] = [csv_row for csv_row in reader]

                except Exception as e:
                    print(f"An error occurred while processing {csv_file}: {e}")
                    csv_content_dict[name_without_extension] = []

                row = {key: val for key, val in row.items() if key not in csv_files}

            for key, value in csv_content_dict.items():
                row[key] = value

        subject = subject_template.render(**row)
        if 'subject_prefix_template' in locals():
            subject = subject_prefix_template.render(**row) + subject

        if 'email_template' in locals():
            email_content = email_template.render(**row)

        if 'html_email_template' in locals():
            html_email_content = html_email_template.render(**row)

        print(f"Sending email with data {row}")
        msg = MIMEMultipart('alternative')
        recipients = []
        if 'emails_to' in row:
            emails_to = row['emails_to']
            msg['To'] = emails_to
            recipients.extend(emails_to.split(EMAIL_ADDRESS_DELIMITER))
        if 'emails_cc' in row:
            emails_cc = row['emails_cc']
            msg['Cc'] = emails_cc
            recipients.extend(emails_cc.split(EMAIL_ADDRESS_DELIMITER))
        if args.recipients:
            recipients = args.recipients.split(EMAIL_ADDRESS_DELIMITER)

        # Email subject
        msg['From'] = args.email
        msg['Subject'] = subject
        msg['Reply-To'] = args.reply
        if has_txt_template:
            msg.attach(MIMEText(email_content, 'plain'))
        if has_html_template:
            msg.attach(MIMEText(html_email_content, 'html'))

        try:
            server = connect(args.smtp_server, args.smtp_port, args.username, args.password, "STARTTLS")
            if server and args.sendemail:
                server.sendmail(args.email, recipients, msg.as_string())
                server.quit()
                print(f"Email sent successfully to {recipients}")
            else:
                #create mail_content.txt file
                file_name = "email_content.txt"
                with open(file_name, 'w') as file:
                    file.write(email_content)
                print(f"Send this email manually:\n \n  {email_content}")
        except Exception as e:
            print(f"Error: unable to send email to {recipients} - {str(e)}")
