import os
import time
from io import BytesIO
from tkinter import Tk, Canvas, BOTH

import requests
import spotipy
import yaml
from PIL import Image, ImageTk
from spotipy.oauth2 import SpotifyOAuth


def get_config():
    try:
        # read in the config file
        with open(os.getcwd() + '\\app_config.yaml') as app_config_file:
            config = yaml.full_load(app_config_file)

        app_config_file.close()
    except OSError:
        print('ERROR trying to read ' + os.getcwd() + '\\app_config.yaml')
    else:
        return config


def create_spotify_obj():
    credentials = config['credentials']

    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        username=credentials['username'],
        client_id=credentials['id'],
        client_secret=credentials['secret'],
        scope=credentials['scope'],
        redirect_uri=credentials['uri']))


def get_current_track(spotify):
    track = spotify.current_user_playing_track()

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


def get_photo_image(src, width, height):
    res = requests.get(src)
    image = Image.open(BytesIO(res.content)).resize((width, height), Image.ANTIALIAS).convert('RGB')
    photo_image = ImageTk.PhotoImage(image, size=())
    return {
        'image': image,
        'photo_image': photo_image
    }


def is_color_bright(image_obj, x, y):
    try:
        r, g, b = image_obj.getpixel((x, y))
        return (r + g + b) / 3 > 127
    except Exception:
        return False


def display_art(spotify):
    root = Tk()
    root.configure(bg=colors['background'], cursor='none')
    root.attributes('-fullscreen', True)
    canvas = Canvas(root,
                    width=dims['display_width'],
                    height=dims['display_height'],
                    bg=colors['background'],
                    bd=0,
                    highlightthickness=0)
    canvas.pack(fill=BOTH, expand=True)

    current_track_name = None
    while True:
        try:
            current_track = get_current_track(spotify)

            if current_track is None:
                current_track_name = None
                root.update()
                time.sleep(config['poll_interval_sleep'])
                continue

            if current_track['track_name'] != current_track_name:
                current_track_name = current_track['track_name']

                # create iamge
                image_obj = get_photo_image(
                    src=current_track['album_art_uri'],
                    width=dims['display_height'],
                    height=dims['display_height']
                )
                canvas.create_image((dims['display_width'] / 2) - (dims['display_height'] / 2), 0,
                                    image=image_obj['photo_image'],
                                    anchor='nw')

                track_bright = is_color_bright(image_obj['image'],
                                               3,
                                               dims['display_height'] - 50)
                artist_bright = is_color_bright(image_obj['image'],
                                                dims['display_height'] - 135,
                                                dims['display_height'] - 3)

                # create text for track
                canvas.create_text((dims['display_width'] / 2 - dims['display_height'] / 2), dims['display_height'] - 50,
                                   text=current_track_name,
                                   fill=colors['track_dark'] if track_bright else colors['track_light'],
                                   font=(fonts['font_family'], fonts['track'], 'bold'),
                                   angle=90,
                                   anchor='nw'
                                   )

                # create text for artist
                canvas.create_text(dims['display_width'] / 2 + dims['display_height'] / 2 - 135, dims['display_height'],
                                   text=current_track['artist'],
                                   fill=colors['artist_dark'] if artist_bright else colors['artist_light'],
                                   font=(fonts['font_family'], fonts['artist'], 'bold'),
                                   anchor='se'
                                   )

                # create text for release date
                canvas.create_text(dims['display_width'] / 2 + dims['display_height'] / 2 - 45, dims['display_height'],
                                   text=current_track['release_date'],
                                   fill=colors['track_dark'] if artist_bright else colors['track_light'],
                                   font=(fonts['font_family'], fonts['release_date']),
                                   anchor='se'
                                   )

                canvas.update()
                canvas.delete("all")
        except Exception:
            canvas.delete("all")
            canvas.update()

        time.sleep(config['poll_interval'])


if __name__ == '__main__':
    config = get_config()
    dims = config['dimensions']
    colors = config['colors']
    fonts = config['fonts']
    display_art(create_spotify_obj())
