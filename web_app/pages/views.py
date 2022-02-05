import service.drive_api as drive_api

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponseRedirect


def home(request):
    pdfs_duplicates = {}
    images_duplicates = {}
    videos_duplicates = {}
    creds = None
    switch_videos = False
    switch_images = False
    switch_pdfs = False
    google_client_id = None
    videos_grid = False
    images_grid = False
    pdfs_grid = False

    if request.method == 'POST':
        switch_videos = request.POST.get('switchCheckVideos', False)
        switch_images = request.POST.get('switchCheckImages', False)
        switch_pdfs = request.POST.get('switchCheckPdfs', False)

        google_client_id = request.COOKIES.get('google_client_id')
        creds = drive_api.auth(google_client_id)

        if switch_pdfs:
            pdfs = drive_api.list_files(creds, query=drive_api.get_mime_type("pdfs"))
            pdfs_duplicates = drive_api.get_duplicated_files_ids(pdfs)
        if switch_images:
            images = drive_api.list_files(creds, query=drive_api.get_mime_type("images"))
            images_duplicates = drive_api.get_duplicated_files_ids(images)
        if switch_videos:
            videos = drive_api.list_files(creds, query=drive_api.get_mime_type("videos"))
            videos_duplicates = drive_api.get_duplicated_files_ids(videos)
        videos_grid = switch_videos
        images_grid = switch_images
        pdfs_grid = switch_pdfs
    else:
        switch_videos = True
        #switch_images = True

    response = render(request, 'home.html', {
        'pdfs': pdfs_duplicates,
        'images': images_duplicates,
        'videos': videos_duplicates,
        'videos_flag': 1 if switch_videos else 0,
        'images_flag': 1 if switch_images else 0,
        'pdfs_flag': 1 if switch_pdfs else 0,
        'videos_grid': 1 if videos_grid else 0,
        'images_grid': 1 if images_grid else 0,
        'pdfs_grid': 1 if pdfs_grid else 0
    })
    if creds and google_client_id is None:
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


def url_redirect(request):
    return HttpResponseRedirect("/drive")
