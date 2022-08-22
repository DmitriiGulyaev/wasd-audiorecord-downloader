import requests
import re
from os import system
import os
from django.template.defaultfilters import slugify as django_slugify
import keyboard

alphabet = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
            'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
            'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ы': 'i', 'э': 'e', 'ю': 'yu',
            'я': 'ya'}
folder_name = 'WASD'
path = folder_name + '\\'
p = 'preform'


def slugify(s):
    """
    Overriding django slugify that allows to use russian words as well.
    """
    return django_slugify(''.join(alphabet.get(w, w) for w in s.lower()))


line = input('https://wasd.tv/<channel_name>/videos?record=<video_id>\nurl: ')

channel_name = re.findall('/(\w+)/', line)[0]
print('channel_name:', channel_name)
record = re.findall(r'\?record=(\d*)', line)[0]
print('record:', record)

session = requests.Session()
res = session.get(f'https://wasd.tv/api/channels/nicknames/{channel_name}')
channel_id = res.json()['result']['channel_id']

print('channel_id:', channel_id)

url = f'https://wasd.tv/api/v2/media-containers?media_container_status=STOPPED&channel_id={channel_id}' \
      f'&media_container_id={record}'
print(url)

res = session.get(url)
result = res.json()['result'][0]

video_name = result['media_container_name']
print('video_name:', video_name)

created_at = '.'.join(result['created_at'][0:10].split('-')[::-1])
print('created_at', created_at)

stream = result['media_container_streams'][0]['stream_media'][0]['media_meta']['media_archive_url']
print(f'video: {stream}')

# audio
audio = re.findall(r'(.*)/index', stream)[0] + f'/tracks-a1/' + re.findall(r'index.*', stream)[0]
print('audio: ', audio)

file_name = slugify(video_name + "_" + created_at)
print('file_name:', file_name)

cover = result['media_container_channel']['channel_image']['small']
print('cover:', cover)

uncut = file_name + '-uncut.mp3'
file_name = file_name + '.mp3'

cutter = '''@echo off\nset start=**:**\nset end=**:**\n''' \
         + f'ffmpeg -ss %start% -to %end% -i {uncut} -c copy {file_name}'

print('Нажми Enter, если верно')
if keyboard.read_key() == "enter":
    system(f'streamlink -o "{p}.aac" "{audio}" best --stream-segment-threads 10') # streamlink -o "{p}.aac" "https://cdn.wasd.tv/live/381873/tracks-a1/index-1661101179-8168.m3u8" best --stream-segment-threads 10
    system(f'ffmpeg -i {p}.aac {p}.mp3') # ffmpeg -i {p}.aac {p}.mp3
    system(f'del {p}.aac') # del {p}.aac
    system(f'ffmpeg -i "{p}.mp3" -i "{cover}" -map 0:0 -map 1:0 -c copy -id3v2_version 3 -metadata:s:v '
           f'title="Album cover" -metadata:s:v comment="Cover (Front)" {path}{uncut}') # ffmpeg -i "{p}.mp3" -i "https://st.wasd.tv/upload/avatars/01b9c117-da50-48d4-b75b-e24c6f5e62c0/original.jpeg" -map 0:0 -map 1:0 -c copy -id3v2_version 3 -metadata:s:v  title="Album cover" -metadata:s:v comment="Cover (Front)" WASD\{uncut}.mp3
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    system(f'{path}{uncut}') # WASD\{uncut}.mp3
    system(f'del {p}.mp3')
    with open(f'{path}cutter.bat', 'w') as f:
        f.write(cutter)
        f.close()