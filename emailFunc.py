try:
    import smtplib, base64, os, pickle, shutil
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import PySimpleGUI as sg

except Exception:
    exit(-1)

SCOPES = "https://www.googleapis.com/auth/gmail.send"

def credentialsInit(credPath):

    #TODO window to get initial creds path
    shutil.copy(credentials, credPath)



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
                credentialsInit(credPath)
            flow = InstalledAppFlow.from_client_secrets_file(credPath, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokenPath, 'wb') as token:
            pickle.dump(creds, token)
        logging.info("Credentials saved.")

    service = build('gmail', 'v1', credentials=creds)
    return service

def createMail():
    pass

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
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        logging.info('Message Id: %s' % message['id'])
        return message
    except Exception as e:
        logging.error("Error" +e)