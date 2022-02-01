import service.drive_api as drive_api

from django.shortcuts import render
from django.shortcuts import redirect


def home(request):
    google_client_id = request.COOKIES.get('google_client_id')
    print(f"get cookie_client_id: {google_client_id}")
    creds = drive_api.auth(google_client_id)

    pdfs = drive_api.list_files(creds, query=drive_api.get_mime_type("pdfs"))
    images = drive_api.list_files(creds, query=drive_api.get_mime_type("images"))
    videos = drive_api.list_files(creds, query=drive_api.get_mime_type("videos"))

    pdfs_duplicates = drive_api.get_duplicated_files_ids(pdfs)
    images_duplicates = drive_api.get_duplicated_files_ids(images)
    videos_duplicates = drive_api.get_duplicated_files_ids(videos)
    response = render(request, 'home.html', {'pdfs': pdfs_duplicates, 'images': images_duplicates, 'videos': videos_duplicates})
    if google_client_id is None:
        print(f"set cookie_client_id: {creds.client_id}")
        response.set_cookie('google_client_id', creds.client_id)
    return response


def delete(request, file_id):
    creds = drive_api.auth()
    print(f"Deleting file: {file_id}")
    drive_api.delete_file(creds, file_id)
    response = redirect('/drive')
    return response


def imprint(request):
    return render(request, 'imprint.html')
