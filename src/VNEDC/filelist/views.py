from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings
import os
import pytz
from datetime import datetime

# Define mappings from user selections to directories
USER_SELECTIONS = {
    'NBR1': 'Z:\\',
    'NBR2': 'Y:\\',
    # Add more mappings as needed
}

def file_list(request, subpath=''):
    # Get the base directory based on user selection
    user_selection = request.GET.get('user_selection', 'NBR1')  # Default to NBR1 if not specified
    base_directory = USER_SELECTIONS.get(user_selection, 'Z:\\')  # Default to Z:\ if selection not found

    directory = os.path.join(base_directory, subpath)
    try:
        entries = os.listdir(directory)
    except FileNotFoundError:
        entries = []
    files = []
    dirs = []
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    for entry in entries:
        entry_path = os.path.join(subpath, entry)
        full_path = os.path.join(directory, entry)
        mod_time = datetime.fromtimestamp(os.path.getmtime(full_path), tz=vn_tz)
        mod_time_str = mod_time.strftime('%d/%m/%Y %H:%M:%S')
        if os.path.isdir(full_path):
            dirs.append((entry_path, mod_time, mod_time_str))
        else:
            files.append((entry_path, mod_time, mod_time_str))

    # Sort directories and files by modification time (newest first)
    dirs.sort(key=lambda x: x[1], reverse=True)
    files.sort(key=lambda x: x[1], reverse=True)

    context = {
        'dirs': [(d[0], d[2]) for d in dirs],
        'files': [(f[0], f[2]) for f in files],
        'subpath': subpath,
        'user_selection': user_selection,
        'user_selections': USER_SELECTIONS.keys(),  # Pass all user selections to template
    }
    return render(request, 'filelist/file_list.html', context)

def download_file(request, subpath):
    file_path = os.path.join(settings.FILE_LIST_DIRECTORY, subpath)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'inline; filename={os.path.basename(file_path)}'
            return response
    raise Http404
