import os
import time
from io import BytesIO
from tkinter import Tk, Frame, Label, font

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

    for i in range(0, len(track['item']['artists'])):
        if i > 0:
            artist_text = artist_text + ', '

        artist_text = artist_text + track['item']['artists'][i]['name']

    return {
        'track_name': track['item']['name'],
        'artist': artist_text,
        'album_art_uri': track['item']['album']['images'][0]['url']
    }


def get_photo_image(src, width, height):
    res = requests.get(src)
    img = Image.open(BytesIO(res.content)).resize((width, height), Image.ANTIALIAS)
    photo_image = ImageTk.PhotoImage(img, size=())
    return photo_image


def display_art(spotify):
    tk = Tk()
    tk.configure(bg=colors['background'], cursor='none')
    tk.attributes('-fullscreen', True)
    frame = Frame(tk, bg=colors['background'], width=dims['display_width'], height=dims['display_height'])
    frame.pack()

    current_track_name = None
    while True:
        time.sleep(config['poll_interval'])
        current_track = get_current_track(spotify)

        if current_track is None:
            tk.update()
            time.sleep(config['poll_interval_sleep'])
            continue

        if current_track['track_name'] != current_track_name:
            current_track_name = current_track['track_name']

            track_font = (fonts['font_family'], fonts['track'], 'bold')
            artist_font = (fonts['font_family'], fonts['artist'])
            track_font_height = font.Font(font=track_font).metrics('linespace')
            artist_font_height = font.Font(font=artist_font).metrics('linespace')

            # create label for track
            track_label = Label(
                frame,
                text=current_track_name,
                bg=colors['background'],
                fg=colors['track'],
                font=track_font
            )
            track_label.place(
                x=dims['display_width'] / 2 - dims['display_height'] / 2,
                y=dims['display_height'],
                anchor='sw'
            )

            # create label for artist
            artist_label = Label(
                frame,
                text=current_track['artist'],
                bg=colors['background'],
                fg=colors['artist'],
                font=artist_font
            )
            artist_label.place(
                x=dims['display_width'] / 2 + dims['display_height'] / 2,
                y=dims['display_height'],
                anchor='se'
            )

            # create label for album art
            photo_image = get_photo_image(
                current_track['album_art_uri'],
                dims['display_height'],
                dims['display_height'] -
                (track_font_height if track_font_height > artist_font_height else artist_font_height) - 1)

            album_art_label = Label(
                frame,
                image=photo_image,
                bd=0
            )
            album_art_label.place(x=(dims['display_width'] / 2) - (dims['display_height'] / 2), y=0)

            tk.update()
            track_label.destroy()
            artist_label.destroy()
            album_art_label.destroy()


if __name__ == '__main__':
    config = get_config()
    dims = config['dimensions']
    colors = config['colors']
    fonts = config['fonts']
    display_art(create_spotify_obj())
