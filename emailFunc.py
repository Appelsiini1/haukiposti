try:
    import smtplib, base64, os.path, pickle
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

except Exception:
    exit(-1)

SCOPES = "https://www.googleapis.com/auth/gmail.send"

def authenticate():
    #google auth
    pass

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