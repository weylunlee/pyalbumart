import os
from io import BytesIO
from tkinter import Tk, Canvas, BOTH

import requests
import spotipy
import yaml
from PIL import Image
from spotipy.oauth2 import SpotifyOAuth

from gui import ImageLabel, TextLabel


class AlbumArt:
    config = None
    dims = None
    colors = None
    fonts = None
    timings = None

    credentials = None
    spotify = None

    root = None
    canvas = None
    album_art_label = None
    track_label = None
    artist_label = None
    release_date_label = None

    current_track_name = None

    @staticmethod
    def load_config():
        try:
            # read in the config file
            with open(os.getcwd() + '/app_config.yaml') as app_config_file:
                AlbumArt.config = yaml.full_load(app_config_file)

            app_config_file.close()
        except OSError:
            print('ERROR trying to read ' + os.getcwd() + '/app_config.yaml')
        else:
            AlbumArt.credentials = AlbumArt.config['credentials']
            AlbumArt.dims = AlbumArt.config['dimensions']
            AlbumArt.colors = AlbumArt.config['colors']
            AlbumArt.fonts = AlbumArt.config['fonts']
            AlbumArt.timings = AlbumArt.config['timings']

    @staticmethod
    def create_spotify_obj():
        AlbumArt.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            username=AlbumArt.credentials['username'],
            client_id=AlbumArt.credentials['id'],
            client_secret=AlbumArt.credentials['secret'],
            scope=AlbumArt.credentials['scope'],
            redirect_uri=AlbumArt.credentials['uri']))

    @staticmethod
    def get_current_track():
        print('spotify::get_track')
        track = AlbumArt.spotify.current_user_playing_track()

        artist_text = ''
        if track is None:
            return None

        item = track['item']

        for i in range(0, len(item['artists'])):
            if i > 0:
                artist_text = artist_text + ', '

            artist_text = artist_text + item['artists'][i]['name']

        return {
            'track_name': item['name'],
            'artist': artist_text,
            'album_art_uri': item['album']['images'][0]['url'],
            'release_date': item['album']['release_date'][0:7]
        }

    @staticmethod
    def get_photo_image(src, width, height):
        res = requests.get(src)
        image = Image.open(BytesIO(res.content)).resize((width, height), Image.ANTIALIAS).convert('RGB')
        return image

    @staticmethod
    def is_color_bright(image_obj, x, y):
        try:
            r, g, b = image_obj.getpixel((x, y))
            return (r + g + b) / 3 > 127
        except Exception:
            return False

    @staticmethod
    def init_gui_components():
        AlbumArt.root = Tk()
        AlbumArt.root.configure(bg='black', cursor='none')
        AlbumArt.root.attributes('-fullscreen', True)
        AlbumArt.canvas = Canvas(AlbumArt.root,
                                 width=AlbumArt.dims['width'],
                                 height=AlbumArt.dims['width'],
                                 bg='black',
                                 bd=0,
                                 highlightthickness=0)
        AlbumArt.canvas.pack(fill=BOTH, expand=True)

        AlbumArt.album_art_label = ImageLabel(AlbumArt.canvas)

        AlbumArt.track_label = TextLabel(AlbumArt.canvas,
                                         40,
                                         AlbumArt.dims['width'],
                                         'sw', 0,
                                         AlbumArt.fonts['font_family'], AlbumArt.fonts['track'])

        AlbumArt.artist_label = TextLabel(AlbumArt.canvas,
                                          AlbumArt.dims['width'],
                                          AlbumArt.dims['width'] - 150,
                                          'ne', 270,
                                          AlbumArt.fonts['font_family'], AlbumArt.fonts['track'])

        AlbumArt.release_date_label = TextLabel(AlbumArt.canvas,
                                                AlbumArt.dims['width'],
                                                AlbumArt.dims['width'] - 130,
                                                'nw', 270,
                                                AlbumArt.fonts['font_family'], AlbumArt.fonts['track'])

    @staticmethod
    def display_art():
        try:
            current_track = AlbumArt.get_current_track()

            if current_track is None:
                AlbumArt.canvas.delete("all")
                AlbumArt.current_track_name = None

                AlbumArt.canvas.update()
                AlbumArt.canvas.wait(AlbumArt.timings['poll_interval_sleep'] * 1000)
            elif current_track['track_name'] != AlbumArt.current_track_name:
                AlbumArt.canvas.delete("all")

                AlbumArt.current_track_name = current_track['track_name']

                # create image
                album_art = AlbumArt.get_photo_image(
                    src=current_track['album_art_uri'],
                    width=AlbumArt.dims['width'],
                    height=AlbumArt.dims['width']
                )

                AlbumArt.album_art_label.show(album_art)

                # set the text labels
                AlbumArt.track_label.show(AlbumArt.current_track_name, None)
                AlbumArt.artist_label.show(current_track['artist'], None)
                AlbumArt.release_date_label.show(current_track['release_date'], None)

                AlbumArt.canvas.update()
        except Exception:
            AlbumArt.canvas.delete("all")
            AlbumArt.canvas.update()

        AlbumArt.canvas.after(AlbumArt.timings['poll_interval'] * 1000, AlbumArt.display_art)

    @staticmethod
    def init():
        # load external configurations
        AlbumArt.load_config()

        # init spotify and tk
        AlbumArt.create_spotify_obj()
        AlbumArt.init_gui_components()


if __name__ == '__main__':
    AlbumArt.init()
    AlbumArt.display_art()
    AlbumArt.root.mainloop()
