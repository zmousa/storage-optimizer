from __future__ import print_function

import os.path
import socket
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def main():
    creds = auth()
    try:
        socket.setdefaulttimeout(600)
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


def auth():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('./token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('./credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('./token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

if __name__ == '__main__':
    main()
