# Author: Kunal Kumar
# Social: twitter.com/l1v1n9h311, instagram.com/prokunal
# Website: procoder.in

from pytube import YouTube
from pytube import Playlist
from math import ceil
import sys
import threading
import logging
import os

log = logging.getLogger("__name__")
ffmpeg_path = r'C:\Users\stream\Desktop\YT-Playlist-Downloader\youtube-playlist-downloader\ffmpeg.exe'
size = 0


def process_playlist(playlist_url):
    try:
        p = Playlist(playlist_url)
        print(f"\nPlaylist Name: {p.title}\nChannel Name: {p.owner}\nTotal Videos: {p.length}")
        
        dir_name = p.title.replace(" ", "")
        directory = r'C:\Users\stream\Desktop\YT-Playlist-Downloader\youtube-playlist-downloader\\' + dir_name
        os.makedirs(directory, exist_ok=True)

        files = set(os.listdir(directory))
        yt_prefixes = {url.split('=')[-1] for url in p.video_urls}
        
        # Delete local videos not present in current playlist
        for file in files:
            file_id = file.split(' ')[0]
            
            if file_id not in yt_prefixes:
                os.remove(os.path.join(directory, file))
                print(f"Deleted local video: {file}")

        links = [url for url in p.video_urls if url.split("=")[-1] not in {file.split(" ")[0] for file in files}]

        if links:
            size = ceil(len(links) / 4)

            def downloader(links):
                for url in links:
                    video_id = url.split('=')[-1]

                    # Prioritize lower-quality video with audio
                    yt = YouTube(url)
                    ys = yt.streams.filter(adaptive=True).filter(mime_type='video/webm').order_by('resolution').desc().first()

                    if ys is None:
                        ys = yt.streams.filter(progressive=False).filter(mime_type='video/mp4').order_by('resolution').desc().first()
                        video_filename = video_id + "_video" + ".mp4"
                        print(ys)
                    # Download video and audio separately
                    else:
                        video_filename = video_id + "_video" + ".webm" # Construct the desired filename
                        print(ys)
                    cleared_video_name = video_id + "_video"
                    
                    video_filepath = ys.download(directory, filename=cleared_video_name)
                    os.rename(video_filepath, os.path.join(directory, cleared_video_name))
                    
                    audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
                    audio_ys = audio_streams.first()
                    print("audio-streams", audio_ys)
                    audio_filename = video_id + "audio" + ".mp4" # Construct the desired filename
                    cleared_audio_name = video_id + "_audio"
                    print("cleared_audio_name", cleared_audio_name)
                    audio_filepath = audio_ys.download(directory, filename=cleared_audio_name)
                    os.rename(audio_filepath, os.path.join(directory, cleared_audio_name))
             
                    # Merge video and audio using ffmpeg
                    output_filename = video_id + "output" + ".mp4"
                    formated_path = video_id + " output" + ".mp4"
                    output_path = os.path.join(directory, output_filename)

                    ffmpeg_command = f"{ffmpeg_path} -i {video_filepath} -i {audio_filepath} -c copy {output_path}"
                    os.system(ffmpeg_command)
                    os.rename(output_path, os.path.join(directory, formated_path))
                
                    # Delete the temporary video and audio files
                    os.remove(audio_filepath) 
                    os.remove(video_filepath)

                print(f"Video downloaded and merged with audio: {output_filename}")

            splitter = [links[i:i + size] for i in range(0, len(links), size)]
            print(splitter)

            threads = []
            for chunk in splitter:
                t = threading.Thread(target=downloader, args=(chunk,))
                threads.append(t)
                
            for t in threads:
                t.start()

        else:
            print("No new videos found in playlist.")

    except Exception as e:
        print(f'Failed to process playlist {playlist_url}: {e}')


if __name__ == "__main__":
    playlists = [
        "https://youtube.com/playlist?list=PLFdHTR758BvdEXF1tZ_3g8glRuev6EC6U&si=PWJk0T8z4eBkkDsc",
        "https://youtube.com/playlist?list=PLFdHTR758Bvd9c7dKV-ZZFQ1jg30ahHFq&si=3Aq3M2m7z5dxgukL"
    ]

    for playlist_url in playlists:
        process_playlist(playlist_url)