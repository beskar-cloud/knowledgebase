import argparse
import csv
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
import ssl
import html2text

"""
python3 generatemail.py -c users.csv -t mail.template -S "$(cat ./g1-g2-migration/templates/subject.txt)" --html2text
"""


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


# Parse command-line arguments
parser = argparse.ArgumentParser(description='Send emails from CSV with Jinja2 template')
parser.add_argument('-c', '--csv', help='Path to CSV file containing email addresses and names')
parser.add_argument('-t', '--template', help='Name of the Jinja2 template located in the folder - there should be two files: template.txt and template.html')
parser.add_argument('--html2text', action='store_true', help='Generate plaintext mail part from HTML template. The *.txt template file will be ignored. Off by default.')
parser.add_argument('-S', '--subject', help='Email subject')

base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
args = parser.parse_args()
# Read email template
has_html_template = False
has_txt_template = False

if not args.subject:
    print("Please provide a subject template string")
    exit(1)
if args.csv is None:
    print("Please provide a CSV file")
    exit(1)

if args.template:
    tempaltes=[args.template]
else:
    directory = base_directory + '/howtos/email_tool/g1-g2-migration/templates'
    tempaltes = [f for f in os.listdir(directory) if '.tmpl' in f or '.html' in f]
    
for template in tempaltes:
    # Determine if the template is HTML or plain text
    if 'directory' in locals():
        template = directory + '/' + template
    if '.html' in template:
        with open(template, 'r') as html_template_file:
            html_template_content = html_template_file.read()
        has_html_template = True
    if has_html_template and args.html2text:
        template_content = convert_html_to_text(html_template_content)
        has_txt_template = True
    elif '.tmpl' in template:
        with open(template, 'r') as template_file:
            template_content = template_file.read()
        has_txt_template = True    

    # Prepare subject template
    subject_template = Template(args.subject)

    if 'template_content' in locals():
        email_template = Template(template_content)
    
    with open(args.csv, 'r') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            msg = MIMEMultipart('alternative')
            subject = subject_template.render(**row)
            csv_files=[]
            for key, value in row.items():            
                if '.csv' in value:
                    csv_files.append(value)
            csv_content_dict = {}
            if csv_files:
                for csv_file in csv_files:
                    name_without_extension = os.path.splitext(csv_file)[0].rsplit('/', 1)[-1]
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

            if 'email_template' in locals():
                email_content = email_template.render(**row)
        
            if 'html_email_template' in locals():
                html_email_content = html_email_template.render(**row)
            file_name = os.path.basename(template)
            file_name = os.path.splitext(file_name)[0] + '-' + row['project_name'] + '.txt'
            with open(file_name, 'w') as file:
                if 'email_template' in locals():
                    file.write(email_content)
    print(f"TEMPLATE NAME: {file_name} \n \n")
    print(f"Send this email manually:\n \n Subject: {subject} \n \n  {email_content}")
    has_html_template = False
