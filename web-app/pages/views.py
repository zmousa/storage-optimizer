import service.drive_api as drive_api

from django.shortcuts import render
from django.shortcuts import redirect


def home(request):
    creds = drive_api.auth()
    pdfs = drive_api.list_files(creds, query=drive_api.get_mime_type("pdfs"))
    images = drive_api.list_files(creds, query=drive_api.get_mime_type("images"))
    videos = drive_api.list_files(creds, query=drive_api.get_mime_type("videos"))

    pdfs_duplicates = drive_api.get_duplicated_files_ids(pdfs)
    images_duplicates = drive_api.get_duplicated_files_ids(images)
    videos_duplicates = drive_api.get_duplicated_files_ids(videos)
    return render(request, 'home.html', {'pdfs': pdfs_duplicates, 'images': images_duplicates, 'videos': videos_duplicates})


def delete(request, file_id):
    creds = drive_api.auth()
    print(f"Deleting file: {file_id}")
    drive_api.delete_file(creds, file_id)
    response = redirect('/drive')
    return response
