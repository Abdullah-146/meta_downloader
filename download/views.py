from django.http import HttpResponse, FileResponse

from django.shortcuts import render, redirect
import yt_dlp
import os
# Create your views here.
# allow this route to handle both GET and POST requests

def download(request):
    message = ""
    if request.method == 'POST':
        video_url = request.POST.get('url')
        quality = request.POST.get('quality')
        # destructure the returned two values
        file_path, details = download_full_video(video_url, quality)
        if file_path:
            # Open the file and serve it as a response
            # Add client side downlaoding
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/octet-stream')
                # Set the Content-Disposition header to trigger a download
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                os.remove(file_path)
                return response
        else:
            message = "Failed to download the video"
    return render(request, 'download.html', context={'message': message})

def download_full_video(video_url, quality):
    yt_opts = {
        'verbose': True,
        'force_keyframes_at_cuts': True,
        'merge_output_format': 'mp4', 
        }

    with yt_dlp.YoutubeDL(yt_opts) as ydl:
        try:
             # Define format selection logic based on quality preference
            if quality == '360':
                # Look for exact 360p format first (consider format 18, 605, 243)
                yt_opts['format'] = '18/605/243'  # Prioritize exact format codes
            elif quality == '720':
                # Look for exact 720p format first (consider format 22, 232, 609, 247)
                yt_opts['format'] = '22/232/609/247'  # Prioritize exact format codes
            else:
                # Handle invalid quality values (optional)
                print(f"Invalid quality: {quality}")
                return None
            info = ydl.extract_info(video_url, download=True)
            # show the output
            # a json file with the video info

            details = {'title':info.get('title', None), 
                       'thumbnail':info.get('thumbnail', None),
                       'uploader':info.get('uploader', None),
                          'duration':info.get('duration', None),
                            'view_count':info.get('view_count', None),
                       }  
            file_path = ydl.prepare_filename(info)
            return file_path, details
        except Exception as e:
            print(e)
            return None