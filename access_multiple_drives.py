from __future__ import print_function

import os.path
import socket
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

####### Requirements #######
# credentials.json & credentials2.json in the folder

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def main():
    socket.setdefaulttimeout(600)

    print("######################################################")
    print("##################### Account 1 ######################")
    print("######################################################")
    account1_creds = auth(tokenFile = './token1.json')    
    list_drive_account_files(account1_creds)

    print("######################################################")
    print("##################### Account 2 ######################")
    print("######################################################")
    account2_creds = auth(tokenFile = './token2.json')
    list_drive_account_files(account2_creds)

    print("######################################################")
    print("##################### Account 3 ######################")
    print("######################################################")
    account2_creds = auth(tokenFile = './token3.json')
    list_drive_account_files(account2_creds)


def auth(credentialsFile = './credentials.json', tokenFile = './token.json'):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(tokenFile):
        creds = Credentials.from_authorized_user_file(tokenFile, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentialsFile, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokenFile, 'w') as token:
            token.write(creds.to_json())
    return creds

def list_drive_account_files(creds):
    try:
        service = build('drive', 'v3', credentials=creds)

        page_token = None
        while True:
            response = service.files().list(q="mimeType='application/pdf'",
                                            spaces='drive',
                                            fields='nextPageToken, files(id, name, size, mimeType, md5Checksum)',
                                            pageToken=page_token).execute()

            for file in response.get('files', []):
                print(u'id: {0} Name: {1} Size: {2} Type: {3} Checksum: {4}'.format(file['id'], file['name'], file['size'], file['mimeType'], file['md5Checksum']))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
            
    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()
