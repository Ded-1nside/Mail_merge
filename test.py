import os  
import pickle  
# imports for Gmail APIs  
from googleapiclient.discovery import build  
from google_auth_oauthlib.flow import InstalledAppFlow  
from google.auth.transport.requests import Request  
# import for encoding/decoding messages in base64  
from base64 import urlsafe_b64decode, urlsafe_b64encode  
# import for dealing with the attachment of MIME types in Gmail  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart  
from email.mime.image import MIMEImage  
from email.mime.audio import MIMEAudio  
from email.mime.base import MIMEBase  
from email.mime.multipart import MIMEMultipart  
from mimetypes import guess_type as guess_mime_type  
#import for spreadsheets
import gspread
  
# Request all access from Gmail, Drive and Spreadsheets APIs and project  
SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets'] # providing the scope for Gmail, Drive and Spreadsheets APIs  
sender_mail = 'nikdanakari@gmail.com' # giving our Gmail Id  
gs = gspread.service_account(filename='creds.json')
  
# using a default function to authenticate Gmail APIs  
def authenticateGmailAPIs():  
    creds = None  
    # authorizing the Gmail APIs with tokens of pickles  
    if os.path.exists("token.pickle"): # using if else statement  
        with open("token.pickle", "rb") as token:  
            creds = pickle.load(token)  
    # if there are no valid credentials available in device, we will let the user sign in manually  
    if not creds or not creds.valid:  
        if creds and creds.expired and creds.refresh_token:  
            creds.refresh(Request())  
        else:  
            flow = InstalledAppFlow.from_client_secrets_file('creds.json', SCOPES) # downloaded credential name  
            creds = flow.run_local_server(port=0) # running credentials  
        # save the credentials for the next run  
        with open("token.pickle", "wb") as token:  
            pickle.dump(creds, token)  
    return build('gmail', 'v1', credentials=creds) # using Gmail to authenticate  
  
# get the Gmail API service by calling the function  
services_GA = authenticateGmailAPIs()  
  
# function to add attachments  
def add_attachment(mail, filename):  
    content_type, encoding = guess_mime_type(filename)  
    if content_type is None or encoding is not None: # defining none file type attachment  
        content_type = 'application/octet-stream'  
    main_type, sub_type = content_type.split('/', 1)  
    if main_type == 'text': # defining text file type attachment  
        fp = open(filename, 'rb')
        msg = MIMEText(fp.read().decode(), _subtype = sub_type)  
        fp.close()   
    elif main_type == 'image': # defining image file type attachment  
        fp = open(filename, 'rb')  
        msg = MIMEImage(fp.read(), _subtype = sub_type)  
        fp.close()  
    elif main_type == 'audio': # defining audio file type attachment  
        fp = open(filename, 'rb')  
        msg = MIMEAudio(fp.read(), _subtype = sub_type) # reading file  
        fp.close()  
    else:  
        fp = open(filename, 'rb')  
        msg = MIMEBase(main_type, sub_type)  
        msg.set_payload(fp.read())  
        fp.close() # closing file  
    filename = os.path.basename(filename)  
    msg.add_header('Content-Disposition', 'attachment', filename = filename)  
    mail.attach(msg) # composing the mail with given attachment  
  
# creating mail function  
def create_mail(reciever_mail, sub_of_mail, body_of_mail, attachments=[]): # various import content of mail as function's parameter  
    # check if there is any attachment in mail or not  
    if not attachments:
        mail = MIMEText(body_of_mail) # Body of Mail  
        mail['to'] = reciever_mail # mail ID of Reciever  
        mail['from'] = sender_mail # our mail ID  
        mail['subject'] = sub_of_mail # Subject of Mail  
    else: 
        mail = MIMEMultipart()  
        mail['to'] = reciever_mail  
        mail['from'] = sender_mail  
        mail['subject'] = sub_of_mail  
        mail.attach(MIMEText(body_of_mail))  
        for filename in attachments:  
            add_attachment(mail, filename)  
    return {'raw': urlsafe_b64encode(mail.as_bytes()).decode()}  
  
# function to send a mail  
def send_mail(services_GA, reciever_mail, sub_of_mail, body_of_mail, attachments=[]):  
    return services_GA.users().messages().send(  
      userId = "me",  
      body = create_mail(reciever_mail, sub_of_mail, body_of_mail, attachments)  
    ).execute() 
  
if __name__ == "__main__":
    spreadsheet_url = input("Type your spreadsheet URL: ")
    sh = gs.open_by_url(spreadsheet_url) # opening table by url
    worksheet = sh.sheet1 # getting access to the first sheet
    recievers = worksheet.col_values(1)
    counter = 0
    for reciever in recievers:
        send_mail(services_GA, reciever, "Sub", "Body", ["test.txt"]) # sending mail
        counter += 1
        worksheet.update_cell(counter, 2, 'sent')