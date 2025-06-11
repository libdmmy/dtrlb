import os
import pathlib
import json

import yt_dlp
ydl_opts = {
    'format': 'bestvideo[height=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height=720]+bestaudio',
    'merge_output_format': 'mp4',
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4',
    }],
    'outtmpl': os.path.join('temp', '%(title)s.%(ext)s'),
    'cookiefile': os.path.join(os.getcwd(), 'ytdl-cookies.txt')
}

ydl = yt_dlp.YoutubeDL(ydl_opts)

def get_information(url: str) -> dict:
    info = ydl.extract_info(url, download=False)
    return info

def download(info) -> pathlib.Path:
    info_path = os.path.join('temp', info['id'])

    with open(info_path, 'x') as f:
        json.dump(info, f)

    ydl.download_with_info_file(info_path)
    os.remove(info_path)

    return pathlib.Path(ydl.prepare_filename(info))