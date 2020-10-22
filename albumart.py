import os
from io import BytesIO
from tkinter import Tk, Canvas, BOTH

import requests
import spotipy
import yaml
from PIL import Image, ImageTk
from spotipy.oauth2 import SpotifyOAuth


class AlbumArt:
    config = None
    dims = None
    colors = None
    fonts = None

    credentials = None
    spotify = None

    root = None
    canvas = None

    current_track_name = None
    prev_image = None
    tk_image = None

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
        image = image.point(lambda p: p * 0.7)
        return image

    @staticmethod
    def is_color_bright(image_obj, x, y):
        try:
            r, g, b = image_obj.getpixel((x, y))
            return (r + g + b) / 3 > 127
        except Exception:
            return False

    @staticmethod
    def init_canvas():
        AlbumArt.root = Tk()
        AlbumArt.root.configure(bg=AlbumArt.colors['background'], cursor='none')
        AlbumArt.root.attributes('-fullscreen', True)
        AlbumArt.canvas = Canvas(AlbumArt.root,
                                 width=AlbumArt.dims['display_width'],
                                 height=AlbumArt.dims['display_height'],
                                 bg=AlbumArt.colors['background'],
                                 bd=0,
                                 highlightthickness=0)
        AlbumArt.canvas.pack(fill=BOTH, expand=True)

    @staticmethod
    def display_art():
        try:
            current_track = AlbumArt.get_current_track()

            if current_track is None:
                AlbumArt.canvas.delete("all")
                AlbumArt.current_track_name = None

                AlbumArt.canvas.update()
                AlbumArt.canvas.wait(AlbumArt.config['poll_interval_sleep'] * 1000)
            elif current_track['track_name'] != AlbumArt.current_track_name:
                AlbumArt.canvas.delete("all")

                AlbumArt.current_track_name = current_track['track_name']

                # create image
                album_art = AlbumArt.get_photo_image(
                    src=current_track['album_art_uri'],
                    width=AlbumArt.dims['display_height'],
                    height=AlbumArt.dims['display_height']
                )

                # fade transition if prev image is exists
                if AlbumArt.prev_image is not None:
                    alpha = 0
                    while 1.0 > alpha:
                        new_img = Image.blend(AlbumArt.prev_image, album_art, alpha)
                        alpha += 0.01
                        tk_image = ImageTk.PhotoImage(new_img)
                        AlbumArt.canvas.create_image(
                            (AlbumArt.dims['display_width'] / 2) - (AlbumArt.dims['display_height'] / 2), 0,
                            image=tk_image,
                            anchor='nw')
                        AlbumArt.canvas.update()
                        AlbumArt.canvas.after(20)

                AlbumArt.tk_image = ImageTk.PhotoImage(album_art)
                AlbumArt.canvas.create_image(
                    (AlbumArt.dims['display_width'] / 2) - (AlbumArt.dims['display_height'] / 2), 0,
                    image=AlbumArt.tk_image,
                    anchor='nw')

                AlbumArt.prev_image = album_art

                artist_bright = AlbumArt.is_color_bright(
                    album_art,
                    3,
                    AlbumArt.dims['display_height'] - 50)
                track_bright = AlbumArt.is_color_bright(
                    album_art,
                    AlbumArt.dims['display_width'] / 2 - AlbumArt.dims[
                        'display_height'] / 2 - 135,
                    AlbumArt.dims['display_height'] - 3)

                # create text for track
                AlbumArt.canvas.create_text(
                    AlbumArt.dims['display_width'] / 2 + AlbumArt.dims['display_height'] / 2 - 45,
                    AlbumArt.dims['display_height'],
                    text=AlbumArt.current_track_name,
                    fill=AlbumArt.colors['track_dark'] if track_bright else AlbumArt.colors['track_light'],
                    font=(AlbumArt.fonts['font_family'], AlbumArt.fonts['track'], 'bold'),
                    anchor='se'
                )

                # create text for artist
                AlbumArt.canvas.create_text(
                    AlbumArt.dims['display_width'] / 2 - AlbumArt.dims['display_height'] / 2,
                    AlbumArt.dims['display_height'] - 130,
                    text=current_track['artist'],
                    fill=AlbumArt.colors['artist_dark'] if artist_bright else AlbumArt.colors[
                        'artist_light'],
                    font=(AlbumArt.fonts['font_family'], AlbumArt.fonts['artist'], 'bold'),
                    angle=90,
                    anchor='nw'
                )

                # create text for release date
                AlbumArt.canvas.create_text(
                    AlbumArt.dims['display_width'] / 2 - AlbumArt.dims['display_height'] / 2,
                    AlbumArt.dims['display_height'] - 50,
                    text=current_track['release_date'],
                    fill=AlbumArt.colors['track_dark'] if artist_bright else AlbumArt.colors['track_light'],
                    font=(AlbumArt.fonts['font_family'], AlbumArt.fonts['release_date']),
                    angle=90,
                    anchor='nw'
                )

                AlbumArt.canvas.update()
        except Exception:
            AlbumArt.canvas.delete("all")
            AlbumArt.canvas.update()

        AlbumArt.canvas.after(AlbumArt.config['poll_interval'] * 1000, AlbumArt.display_art)

    @staticmethod
    def init():
        # load external configurations
        AlbumArt.load_config()

        # init spotify and tk
        AlbumArt.create_spotify_obj()
        AlbumArt.init_canvas()


if __name__ == '__main__':
    AlbumArt.init()
    AlbumArt.display_art()
    AlbumArt.root.mainloop()
