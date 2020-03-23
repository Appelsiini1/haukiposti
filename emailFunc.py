try:
    import smtplib, base64, os, pickle, shutil, logging
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email.mime.audio import MIMEAudio
    from email.mime.image import MIMEImage
    import PySimpleGUI as sg

except Exception:
    exit(-1)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def credentialsInit(credPath):
    pass
    #TODO window to get initial creds path
    #shutil.copy(credentials, credPath)



def authenticate():
    """Authenticate user. Returns authorized service object.
    On first run, this will copy the credentials to working directory for future use.
    """
    logging.info("Begin authentication")
    credPath = os.path.join((os.getenv("APPDATA") + "\\Haukiposti"), "credentials.json")
    tokenPath = os.path.join((os.getenv("APPDATA") + "\\Haukiposti"), "token.pickle")

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(tokenPath):
        with open(tokenPath, 'rb') as token:
            creds = pickle.load(token)
            logging.info("Credentials loaded")
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            logging.info("Credentials refreshed.")
        else:
            if os.path.exists(credPath) == False:
                #TODO
                #credentialsInit(credPath)
                credPath = "credentials.json"
            flow = InstalledAppFlow.from_client_secrets_file(credPath, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokenPath, 'wb') as token:
            pickle.dump(creds, token)
        logging.info("Credentials saved.")

    service = build('gmail', 'v1', credentials=creds)

    # results = service.users().labels().list(userId='me').execute()
    # labels = results.get('labels', [])

    # if not labels:
    #     print('No labels found.')
    # else:
    #     print('Labels:')
    #     for label in labels:
    #         print(label['name'])

    return service

def createMail(sender, to, subject, message_text, file):
    """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
    file: The path to the file to be attached.

  Returns:
    An object containing a base64url encoded email object.
  """
    message = MIMEMultipart()
    message['bcc'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    content_type, encoding = mimetypes.guess_type(file)

    if content_type is None or encoding is not None:
      content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(file, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(file, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(file, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(file, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    filename = os.path.basename(file)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string())}


def sendMail(service, user_id, message):
    """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
    try:
        message = (service.users().messages().send(userId='me', body=message).execute())
        logging.info('Message Id: %s' % message['id'])
        return message
    except Exception as e:
        logging.error("Error: " +e)