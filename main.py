import vlc
import yt_dlp
import os
from pytubefix import Channel
import json
import random

class VODs:
    def __init__(self):
        self.player = vlc.Instance()
        self.media_player = self.player.media_player_new()
        self.ydl_opts = {'outtmpl':'vods/queue/%(title)s.%(ext)s', 'format':"bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"}
        self.url = "https://www.youtube.com/@Neuro-samaUnofficialVODs"
        self.video_queue = None

    def get_playlist(self):
        #Open JSON files
        with open("vods.json", "r+") as vj:
            vods_data = json.load(vj)
            #Get Playlist
            playlist = Channel(self.url)
            vods_array = vods_data['vods']
            #Go through the playlist array and add unwatched videos & videos not added in the vod_data array (new videos)
            total_added = 0
            for v in playlist.videos:
                if v.watch_url not in vods_data['vods']:
                    vods_array.append(v.watch_url)
                    total_added += 1
            data = {"vods": vods_array}
            vj.truncate()
            vj.seek(0)
            json.dump(data, vj)
        print(f"Added {total_added} new video(s).")
        
    def get_url(self):
        #Open JSON file and get a random URL
        with open("vods.json", "r+") as vj:
            vods_data = json.load(vj)
            vj.seek(0)
            vods_array = vods_data['vods']
            url = random.choice(vods_array)
            # Remove URL
            vods_array.remove(url)
            data = {"vods": vods_array}
            vj.truncate()
            json.dump(data, vj)
        return url

    def get_video(self):
        #Get the URL to download
        url = self.get_url()
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([url])

    def set_vod(self):
        video = os.listdir("vods/queue/")[0]
        os.replace(f"vods/queue/{video}", f"vods/watched/{video}")

        media = vlc.Media(f"vods/watched/{video}")
        self.media_player.set_media(media)

    def start_player(self):
        while True:
            self.video_queue = len(os.listdir("vods/queue/"))
            if self.media_player.is_playing() == 0 and self.video_queue != 0:
                self.set_vod()
                # Play media
                self.media_player.play()
            elif self.video_queue == 0:
                self.get_video()


      
vods = VODs()
vods.get_playlist()
vods.start_player()

