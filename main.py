import vlc
import yt_dlp
import os
from pytube import Playlist
import json
import random
import time

class VODs:
    def __init__(self):
        self.player = vlc.Instance()
        self.media_player = self.player.media_player_new()
        self.ydl_opts = {'outtmpl':'VODs/recent_%(title)s.%(ext)s', 'format':"best[ext=mp4]"}
        self.url = "https://www.youtube.com/watch?v=-9D3b3G-2YQ&list=PLyuakwzSUr6ARBtMZkYsde8TWgfn9olm7"
        self.video_queue = None

    def get_playlist(self):
        #Open JSON files
        with open("VODs\\vods.json", "r") as vj:
            vods_data = json.load(vj)
        with open("VODs\\watched.json", "r") as wj:
            watched_data = json.load(wj)
        #Get Playlist
        playlist = Playlist(self.url)
        vods_array = vods_data['vods']
        #Go through the playlist array and add unwatched videos & videos not added in the vod_data array (new videos)
        total_added = 0
        for v in playlist:
            if v not in vods_data['vods'] and v not in watched_data['watched']:
                vods_array.append(v)
                total_added += 1
        #Write to vods.json
        with open("VODS\\vods.json", "w") as vj:
            data = {"vods": vods_array}
            json.dump(data, vj)
        print(f"Added {total_added} new video(s).")
        
    def get_url(self):
        #Open JSON file and get a random URL
        with open("VODs\\vods.json", "r") as vj:
            vods_data = json.load(vj)
        vods_array = vods_data['vods']
        array_length = len(vods_array)
        #pure hatred
        if array_length != 0: array_length -= 1
        random_n = random.randint(0 , array_length)
        return vods_array[random_n]

    def get_video(self, skip=None):
        #Get the URL to download
        if not skip:
            url = self.get_url()
            self.video_queue = url
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([url])
        #Get the name of the file
        for f in os.listdir("VODs"):
            if f.startswith("recent"):
                return f

    def set_vod(self, skip=None):
        #If skip is `true`, dont download video
        if not skip:
            video = self.get_video()
        else:
            video = self.get_video(skip=skip)
        new_video = video.replace("recent_", "")
        os.rename(f"VODs\\{video}", f"VODs\\{new_video}")

        media = vlc.Media(f"VODs\\{new_video}")
        self.media_player.set_media(media)

    def start_player(self):
        while True:
            if self.media_player.is_playing() == 0:
                #Set VOD and start player
                if not self.video_queue:
                    self.set_vod()
                else:
                    self.set_vod(skip=True)
                #Remove last video played
                with open("VODs\\vods.json", "r") as vj:
                    vods_data = json.load(vj)
                    vods_array = vods_data["vods"]
                    vods_array.remove(self.video_queue)
                    data = {"vods": vods_array}
                    with open("VODs\\vods.json", "w") as vj:
                        json.dump(data, vj)
                #Add to watched list
                with open("VODs\\watched.json", "r") as wj:
                    watched_data = json.load(wj)
                    watched_array = watched_data['watched']
                    watched_array.append(self.video_queue)
                    data = {"watched": watched_array}
                    with open("VODs\\watched.json", "w") as wj:
                        json.dump(data, wj)
                    time.sleep(1)
                    self.media_player.play()
                self.video_queue = None
                time.sleep(0.1)
            elif not self.video_queue:
                self.get_video()


            
vods = VODs()
vods.get_playlist()
vods.start_player()