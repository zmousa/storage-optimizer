from __future__ import print_function
import pandas as pd
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
SCOPES = ['https://www.googleapis.com/auth/drive.metadata', 'https://www.googleapis.com/auth/drive']


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

def list_drive_account_files(creds,mimeType,drive_account="main_account"):
    try:
        service = build('drive', 'v3', credentials=creds)

        page_token = None
        files_list_df=pd.DataFrame()
        ## searching by files types, hardcoded
        if mimeType=="images":
            q="mimeType='image/jpeg' or mimeType='image/png' or mimeType='image/heic' or mimeType='image/heif'"
        elif mimeType=="videos":
            q="mimeType='video/mp4' or mimeType='video/x-msvideo' or mimeType='video/x-ms-wmv'"
        elif mimeType=="pdfs":
            q="mimeType='application/pdf'"
        elif mimeType=="compressed_files":
            q="mimeType='application/zip' or mimeType='application/rar' or mimeType='application/tar'"
        else:
            q=""
            
        while True:
            ## Mimetypes:  ["application/pdf","image/jpeg","image/png","application/zip","application/rar","application/tar","video/mp4","video/x-msvideo","video/x-ms-wmv"]
            response = service.files().list(q=q,
                                            spaces='drive',
                                            fields='nextPageToken, files(id, name, size, mimeType, md5Checksum, createdTime, modifiedTime)',
                                            pageToken=page_token).execute()

            ## save it into Pandas
            files_list_df=files_list_df.append(pd.DataFrame(response.get('files', [])),ignore_index=True)
            #print(files_list_df)
            #for file in response.get('files', []):
                
            ##    print(u'id: {0} Name: {1} Size: {2} Type: {3} Checksum: {4}'.format(file['id'], file['name'], file['size'], file['mimeType'], file['md5Checksum']))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        ## add account column into the files data frame
        files_list_df["account"]=drive_account
        return files_list_df
    except HttpError as error:
        print(f'An error occurred: {error}')
        
## access two accounts to get the files list by mimetype ( images, videos, pdfs, compressed_files)
def get_multiple_account_files_by_type(account1_creds,account2_creds,file_type="videos"):
    account1_creds = auth(tokenFile = './token1.json')    
    account1_files_df=list_drive_account_files(account1_creds,file_type)
    #account1_files_df
    if(account2_creds is not None):
        account2_creds = auth(tokenFile = './token2.json')
        account2_files_df=list_drive_account_files(account2_creds,file_type,"account_2")
        #account2_files_df

    ## merge the two accounts files into one data frame 
    return account2_files_df.append(account1_files_df,ignore_index=True)

## this function to return the Files Ids that needs to pass through too Drive API for deletiion.
## Input: files_list_df: teh data frame the contains all the files retrieved from Drive account. It includes all duplicates without grouping
## returns only the files Ids and teh accounts belongs to
def get_duplicated_files_ids(files_list_df):
    ## convert column size to integer for sorting purposes
    files_list_df["size"] = pd.to_numeric(files_list_df["size"])
    ## group the files by md5checksum and keep only the duplicated files. sorting them to keep the oldest created file as the first occurance version of the duplicaes
    files_list_df=files_list_df[files_list_df.md5Checksum.isin(files_list_df.groupby("md5Checksum").filter(lambda x: len(x) > 1)["md5Checksum"])].sort_values(by=['size','md5Checksum',"createdTime"],ascending=[False,True,True])
    
    ## find the duplicated files(based on md5checksum) and return the rown indices without the first occurance 
    duplicated_indices=files_list_df.duplicated(subset=['md5Checksum'],keep='first')
    duplicated_indices=duplicated_indices[duplicated_indices != False].index.values.tolist()
    #duplicated_indices
    
    ## return the file ids for the duplicated files that needs to be deleted
    return files_list_df.loc[duplicated_indices,['id',"account"]].values.tolist()

## Permanently delete a file, skipping the trash.
def delete_file(creds, file_id):
    try:
        service = build('drive', 'v3', credentials=creds)
        service.files().delete(fileId=file_id).execute()
    except HttpError as error:
        print(f'An error occurred: {error}')

def main():
    # socket.setdefaulttimeout(600)
    
    ## file_type: images, videos, pdfs, compressed_files
    ## Mimetypes:  ["application/pdf","image/jpeg","image/png","video/mp4","video/x-msvideo","video/x-ms-wmv","application/zip","application/rar","application/tar"]
    account1_creds = auth(tokenFile = './token1.json')  
    account2_creds = auth(tokenFile = './token2.json')
    files_list_df=get_multiple_account_files_by_type(account1_creds,account2_creds,file_type="videos")
    print(get_duplicated_files_ids(files_list_df))
    
if __name__ == '__main__':
    main()