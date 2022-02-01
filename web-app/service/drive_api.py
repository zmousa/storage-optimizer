from __future__ import print_function

import os.path
import socket
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata', 'https://www.googleapis.com/auth/drive']


class DriveFile:
    def __init__(self, file_id, name, mime_type, create_date, modified_date, md5_checksum, size):
        self.file_id = file_id
        self.name = name
        self.size = size
        self.mime_type = mime_type
        self.md5_checksum = md5_checksum
        self.create_date = create_date
        self.modified_date = modified_date

    def __str__(self):
        return f"File({self.file_id}, {self.name}, {self.size}, {self.mime_type}, {self.md5_checksum}, {self.create_date}, {self.modified_date})"


def get_mime_type(mimeType):
    if mimeType == "images":
        return "mimeType='image/jpeg' or mimeType='image/png' or mimeType='image/heic' or mimeType='image/heif'"
    elif mimeType == "videos":
        return "mimeType='video/mp4' or mimeType='video/x-msvideo' or mimeType='video/x-ms-wmv'"
    elif mimeType == "pdfs":
        return "mimeType='application/pdf'"
    elif mimeType == "compressed_files":
        return "mimeType='application/zip' or mimeType='application/rar' or mimeType='application/tar'"
    else:
        return ""


def auth(google_client_id=None):
    file_name = ""
    if google_client_id is not None:
        file_name = f"./tokens/{google_client_id}.json"

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if google_client_id is not None and os.path.exists(file_name):
        creds = Credentials.from_authorized_user_file(file_name, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('./credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(f"./tokens/{creds.client_id}.json", 'w') as token:
            token.write(creds.to_json())
    return creds


def list_files(creds, query):
    files_list_df = pd.DataFrame()
    try:
        socket.setdefaulttimeout(600)
        service = build('drive', 'v3', credentials=creds)
        page_token = None
        while True:
            response = service.files().list(q=query,
                                            spaces='drive',
                                            fields='nextPageToken, files(id, name, size, mimeType, md5Checksum, createdTime, modifiedTime)',
                                            pageToken=page_token).execute()
            files_list_df = files_list_df.append(pd.DataFrame(response.get('files', [])), ignore_index=True)
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
    except HttpError as error:
        print(f'An error occurred: {error}')
    return files_list_df


def get_duplicated_files_ids(files_list_df):
    if files_list_df.empty:
        return []
    # convert column size to integer for sorting purposes
    files_list_df["size"] = round(pd.to_numeric(files_list_df["size"]) / 1024 / 1024, 3)

    files_list_df["createdTime"] = files_list_df.apply(lambda row: str(row["createdTime"])[:-5].replace('T', ' '), axis=1)
    files_list_df["modifiedTime"] = files_list_df.apply(lambda row: str(row["modifiedTime"])[:-5].replace('T', ' '), axis=1)
    # group the files by md5checksum and keep only the duplicated files.
    # sorting them to keep the oldest created file as the first occurrence version of the duplicates
    files_list_df = files_list_df[files_list_df.md5Checksum.isin(
        files_list_df.groupby("md5Checksum").filter(lambda x: len(x) > 1)["md5Checksum"])].sort_values(
        by=['size', 'md5Checksum', "createdTime"], ascending=[False, True, True])

    # find the duplicated files(based on md5checksum) and return the rows indices without the first occurrence
    duplicated_indices = files_list_df.duplicated(subset=['md5Checksum'], keep='first')
    duplicated_indices = duplicated_indices[duplicated_indices != False].index.values.tolist()
    duplicated_indices = files_list_df.loc[duplicated_indices].values.tolist()

    drive_duplicates = []
    for file in duplicated_indices:
        # print(file[0], file[1], file[2], file[3], file[4], file[5], file[6])
        drive_duplicates.append(DriveFile(file[0], file[1], file[2], file[3], file[4], file[5], file[6]))

    duplication_dict = {}
    for file in drive_duplicates:
        if file.md5_checksum in duplication_dict:
            duplication_dict[file.md5_checksum].append(file)
        else:
            duplication_dict[file.md5_checksum] = [file]

    return duplication_dict


# Permanently delete a file, skipping the trash.
def delete_file(creds, file_id):
    try:
        service = build('drive', 'v3', credentials=creds)
        service.files().delete(fileId=file_id).execute()
    except HttpError as error:
        print(f'An error occurred: {error}')
