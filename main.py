import vlc
import yt_dlp
import os
from pytubefix import Channel, Playlist # playlist is used for testing
import json
import random
import time

class VODs:
    def __init__(self):
        self.player = vlc.Instance()
        self.media_player = self.player.media_player_new()
        self.ydl_opts = {'outtmpl':'vods/queue/%(title)s.%(ext)s', 'format':"bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"}
        self.url = "https://www.youtube.com/@NArchiver"
        self.video_queue = None

        with open("cfg.json", "r") as settings:
            cfg = json.load(settings)
            self.volume = cfg["volume"]
            self.skip = False

    def get_playlist(self):
        #Open JSON files
        with open("vods.json", "r+") as vj:
            vods_data = json.load(vj)
            #Get Playlist
            playlist = Playlist(self.url)
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
        
        with open("cfg.json", "r+") as settings:
            cfg = json.load(settings)
            cfg["current_vod"]["url"] = url
            settings.seek(0)
            settings.truncate()
            json.dump(cfg, settings)
        return url

    def get_video(self):
        #Get the URL to download
        url = self.get_url()
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([url])

    def set_vod(self):
        video = os.listdir("vods/queue/")[0]
        with open("cfg.json", "r+") as settings:
            cfg = json.load(settings)
            cfg["current_vod"]["title"] = video
            settings.seek(0)
            settings.truncate()
            json.dump(cfg, settings)

        os.replace(f"vods/queue/{video}", f"vods/watched/{video}")

        media = vlc.Media(f"vods/watched/{video}")
        self.media_player.set_media(media)

    def start_player(self):
        while True:
            with open("cfg.json", "r+") as settings:
                cfg = json.load(settings)
                if self.volume != cfg["volume"]:
                    self.volume = cfg["volume"]
                    self.media_player.audio_set_volume(self.volume)
                if cfg["skip"]:
                    self.set_vod()

            self.video_queue = len(os.listdir("vods/queue/"))
            if self.media_player.is_playing() == 0 and self.video_queue != 0:
                self.set_vod()
                # Play media
                self.media_player.play()
                time.sleep(0.1) # this prevents everything from breaking

                #Remove media in watched folder, except currently playing media
                for f in os.listdir("vods/watched"):
                    try:
                        os.remove(f"vods/watched/{f}")
                    except: pass 
            elif self.video_queue == 0:
                self.get_video()


      
vods = VODs()
vods.get_playlist()
vods.start_player()

