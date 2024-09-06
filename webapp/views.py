from urllib import request
from django.http import JsonResponse
from django.shortcuts import render
import os
from django.shortcuts import HttpResponse
from django.urls import reverse
import shutil
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.urls import reverse
import os
import shutil
import uuid
import uuid
import datetime
from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import default_storage
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
import pysrt
import logging
import os
import shutil
from pathlib import Path
from webapp.utils import generate_srt_from_txt_and_audio, load_subtitles_from_file, process_multiple_video_segment_replacements, remove_all_files_in_directory, subriptime_to_seconds

MAE_THRESHOLD: float = 3.0
GLITCH_IGNORE_THRESHOLD: float = 0.1

def generate_unique_id():
    return str(uuid.uuid4())

def generate_datetime_alias():
    current_time = datetime.datetime.now()
    return current_time.strftime("%Y-%m-%d_%H-%M-%S")

def index(request):
    # Render HTML template similar to render_template_string in Flask
    return render(request, 'index.html')  # Save your template in webapp/templates/index.html


def app(request):
    # Render HTML template similar to render_template_string in Flask
    return render(request, 'app.html')  # Save your template in webapp/templates/index.html


def video_processing_page(request):
    # Clear the session replacements at the start of the new session
    if 'replacements' in request.session:
        del request.session['replacements']
    
    return render(request, 'video_processing.html')


def get_srt_index(request):
    # Extract 'time' from the request's GET parameters
    current_time = float(request.GET.get('time'))
    
    # Load subtitles from a file (adapt the path as needed)
    subtitles = load_subtitles_from_file(Path('uploads/original_subtitles.srt'))
    
    # Iterate over the subtitles to find the one matching the current time
    for index, subtitle in enumerate(subtitles):
        start_time = subriptime_to_seconds(subtitle.start)
        end_time = subriptime_to_seconds(subtitle.end)
        if start_time <= current_time <= end_time:
            return JsonResponse({"srt_index": index})
    
    # Return -1 if no matching subtitle is found
    return JsonResponse({"srt_index": -1})


def process(request):
    if request.method == 'POST':
        static_out_file_server = os.path.join(settings.STATIC_ROOT, 'output_root')
        tmp = os.path.join(settings.BASE_DIR, 'tmp')
        final_out_path = os.path.join(static_out_file_server, 'final')
        outpath = os.path.join(static_out_file_server, 'output')

        try:
            # Cleanup old files
            remove_all_files_in_directory(os.path.join(outpath, 'videos'))
            remove_all_files_in_directory(os.path.join(outpath, 'audios'))
            remove_all_files_in_directory(final_out_path)

            if os.path.exists(tmp):
                tmp_dirs = os.listdir(tmp)
                for dir in tmp_dirs:
                    remove_all_files_in_directory(os.path.join(tmp, dir))
                shutil.rmtree(tmp)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'An error occurred during cleanup: {e}'}, status=500)

        try:
            # Create necessary directories
            os.makedirs(outpath, exist_ok=True)
            os.makedirs(os.path.join(outpath, 'audios'), exist_ok=True)
            os.makedirs(os.path.join(outpath, 'videos'), exist_ok=True)
            os.makedirs(final_out_path, exist_ok=True)
            os.makedirs(tmp, exist_ok=True)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'An error occurred during directory creation: {e}'}, status=500)

        unique_special_id = os.path.join(tmp, generate_unique_id())
        os.makedirs(unique_special_id, exist_ok=True)
        video_dir = os.path.join(unique_special_id, "video")
        clips_dir = os.path.join(unique_special_id, "clips")
        mp3_dir = os.path.join(unique_special_id, "mp3")
        text_dir = os.path.join(unique_special_id, "text")
        font_dir = os.path.join(unique_special_id, "font")
        os.makedirs(video_dir, exist_ok=True)
        os.makedirs(clips_dir, exist_ok=True)
        os.makedirs(mp3_dir, exist_ok=True)
        os.makedirs(text_dir, exist_ok=True)
        os.makedirs(font_dir, exist_ok=True)

        try:
            # Save uploaded files
            video_file = request.FILES.get('video_file')
            mp3_file = request.FILES.get('mp3_file')
            text_file = request.FILES.get('text_file')
            font_file = request.FILES.get('font_file')

            if not all([video_file, mp3_file, text_file, font_file]):
                return JsonResponse({'status': 'error', 'message': 'Missing required files'}, status=400)

            video_file_path = default_storage.save(os.path.join(video_dir, video_file.name), ContentFile(video_file.read()))
            mp3_file_path = default_storage.save(os.path.join(mp3_dir, mp3_file.name), ContentFile(mp3_file.read()))
            text_file_path = default_storage.save(os.path.join(text_dir, text_file.name), ContentFile(text_file.read()))
            font_file_path = default_storage.save(os.path.join(font_dir, font_file.name), ContentFile(font_file.read()))

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'An error occurred while saving files: {e}'}, status=500)

        # New parameters
        global_font_size = int(request.POST.get('font_size', 20))
        global_box_color = str(request.POST.get('font_color'))
        global_bg_color = str(request.POST.get('bg_color'))
        global_margin = int(request.POST.get('margin', 26)) 
        global_font_file_path = font_file_path

        if not global_font_size or not global_box_color or not global_bg_color:
            return JsonResponse({'status': 'error', 'message': 'Missing required form data'}, status=400)

        try:
            # Generate the SRT file from TXT and MP3 files
            srt_file = generate_srt_from_txt_and_audio(text_file_path, mp3_file_path, tmp)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Failed to generate SRT file: {e}'}, status=500)

        # Move the SRT file to uploads directory for further processing
        final_srt_path = os.path.join(settings.MEDIA_ROOT, 'original_subtitles.srt')
        shutil.move(srt_file, final_srt_path)

        # Move the video file to uploads directory for further processing
        final_video_path = os.path.join(settings.MEDIA_ROOT, 'original_video.mp4')
        shutil.move(video_file_path, final_video_path)

        # Return JSON response with success message
        response = {
            'status': 'success',
            'message': 'Files processed successfully',
            'redirect': reverse('video_processing_page')
        }
        return JsonResponse(response)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    
    
def process_video(request):
    if request.method == 'POST':
        # Paths for files
        original_video_path = os.path.join(settings.MEDIA_ROOT, 'original_video.mp4')
        subtitles_path = os.path.join(settings.MEDIA_ROOT, 'original_subtitles.srt')

        # Load all replacements from session
        replacements = request.session.get('replacements', [])
        
        # Debug print to check if replacements exist
        print(f"[DEBUG] Replacements: {replacements}", flush=True)
        
        # Ensure we have replacements to process
        if not replacements:
            return JsonResponse({"status": "error", "message": "No segments to replace"}, status=400)
        
        # Check if font file exists
        global_font_file_path = settings.GLOBAL_FONT_FILE_PATH
        if not os.path.exists(global_font_file_path):
            print(f"[ERROR] Font file not found at: {global_font_file_path}", flush=True)
            return JsonResponse({"status": "error", "message": "Font file not found"}, status=400)
        else:
            print(f"[DEBUG] Font file was found at: {global_font_file_path}", flush=True)

        try:
            # Process all replacements
            process_multiple_video_segment_replacements(
                original_video_path=original_video_path,
                subtitles_path=subtitles_path,
                replacements=replacements,
                font_path=global_font_file_path,
                font_size=int(request.session.get('global_font_size', 20)),
                font_color=str(request.session.get('global_box_color')),
                bg_color=str(request.session.get('global_bg_color')),
                margin=int(request.session.get('global_margin', 26))
            )

            # Clear the session replacements after processing
            request.session.pop('replacements', None)

            return JsonResponse({"status": "success", "message": "Video processing and segment replacement completed successfully."})

        except Exception as e:
            print(f"[ERROR] Processing failed: {e}", flush=True)
            return JsonResponse({"status": "error", "message": f"Processing failed: {e}"}, status=500)

    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)
    
    
def upload_new_scene(request):
    if request.method == 'POST':
        srt_index = int(request.POST.get('srt_index'))
        new_scene = request.FILES.get('scene')

        if not new_scene:
            return JsonResponse({"status": "error", "message": "No scene file uploaded"}, status=400)
        
        temp_scene_path = os.path.join(settings.MEDIA_ROOT, new_scene.name)
        
        with open(temp_scene_path, 'wb+') as destination:
            for chunk in new_scene.chunks():
                destination.write(chunk)

        # Store the replacement details in session
        replacements = request.session.get('replacements', [])
        
        if not any(r['srt_index'] == srt_index for r in replacements):
            replacements.append({
                'srt_index': srt_index,
                'scene_path': temp_scene_path
            })
            request.session['replacements'] = replacements

        # Debug prints
        print(f"[DEBUG] Uploaded SRT Index: {srt_index}", flush=True)
        print(f"[DEBUG] Temporary Scene Path: {temp_scene_path}", flush=True)
        print(f"[DEBUG] Current Replacements in Session: {request.session['replacements']}", flush=True)

        return HttpResponse("Scene uploaded and stored for replacement.")

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)




def download_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    
    if not os.path.exists(file_path):
        return HttpResponse("File not found", status=404)
    
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response