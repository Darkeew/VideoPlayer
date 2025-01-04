import vlc
import yt_dlp
import os
from pytube import Playlist
import json
import random

class VODs:
    def __init__(self):
        self.player = vlc.Instance()
        self.media_player = self.player.media_player_new()
        self.ydl_opts = {'outtmpl':'VODs/video.mp4', 'format':"best[ext=mp4]"}
        self.url = "https://www.youtube.com/watch?v=D8T7vBBNkT4&list=PL3HIihraebSjjFa_ow3WoEKseRmu1Z5k6"
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

    def get_video(self, skip = None):
        #Check for videos in the folder, this is ignored if `skip` is true.
        if not skip:
            for f in os.listdir('VODs'):
                if ".mp4" in f or ".part" in f:
                    os.remove(f"VODs\\{f}")
        #Get the URL to download
        url = self.get_url()
        self.video_queue = url
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([url])
        return "VODs\\video.mp4"

    def set_vod(self):
        #Transform the video into a VLC media object
        video = self.get_video()
        os.rename(video, "VODs\\playing.mp4")
        media = vlc.Media(video)
        #Add to the media player
        self.media_player.set_media(media)

    def start_player(self):
        while True:
            if self.media_player.is_playing() == 0:
                #Set VOD and start player
                self.set_vod()
                self.media_player.play()
                #Remove last video played
                with open("VODs\\vods.json", "r+") as vj:
                    vods_data = json.load(vj)
                    vods_array = vods_data["vods"]
                    vods_array.remove(self.video_queue)
                    data = {"vods": vods_array}
                    json.dump(data, vj)
                #Add to watched list
                with open("VODs\\watched.json", "r") as wj:
                    watched_data = json.load(wj)
                    watched_array = watched_data['watched']
                    watched_array.append(self.video_queue)
                    data = {"watched": watched_array}
                    json.dump(data, wj)
                self.video_queue = None
            elif not self.video_queue:
                self.get_video(self, skip=True)

            
vods = VODs()
vods.start_player()