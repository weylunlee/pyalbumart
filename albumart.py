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
    img = Image.open(BytesIO(res.content)).resize((width, height), Image.ANTIALIAS)
    photo_image = ImageTk.PhotoImage(img, size=())
    return photo_image


def create_image_label(frame, photo_image, x, y):
    label = Label(frame, image=photo_image, bd=0)
    label.place(x=x, y=y)
    return label


def create_text_label(frame, text, bg, fg, text_font, x, y, anchor):
    label = Label(frame, text=text, bg=bg, fg=fg, font=text_font)
    label.place(x=x, y=y, anchor=anchor)
    return label


def display_art(spotify):
    tk = Tk()
    tk.configure(bg=colors['background'], cursor='none')
    tk.attributes('-fullscreen', True)
    frame = Frame(tk, bg=colors['background'], width=dims['display_width'], height=dims['display_height'])
    frame.pack()

    current_track_name = None
    while True:
        current_track = get_current_track(spotify)

        if current_track is None:
            current_track_name = None
            tk.update()
            time.sleep(config['poll_interval_sleep'])
            continue

        if current_track['track_name'] != current_track_name:
            current_track_name = current_track['track_name']

            track_font = (fonts['font_family'], fonts['track'], 'bold')
            artist_font = (fonts['font_family'], fonts['artist'])
            release_date_font = (fonts['font_family'], fonts['release_date'])
            track_font_height = font.Font(font=track_font).metrics('linespace')
            artist_font_height = font.Font(font=artist_font).metrics('linespace')
            release_date__font_height = font.Font(font=release_date_font).metrics('linespace')
            photo_height = dims['display_height'] - max(track_font_height + release_date__font_height, artist_font_height)

            # create label for album art
            photo_image = get_photo_image(
                src=current_track['album_art_uri'],
                width=dims['display_height'],
                height=photo_height
            )

            album_art_label = create_image_label(
                frame,
                photo_image=photo_image,
                x=(dims['display_width'] / 2) - (dims['display_height'] / 2),
                y=0
            )

            # create label for track
            track_label = create_text_label(
                frame=frame,
                text=current_track_name,
                bg=colors['background'],
                fg=colors['track'],
                text_font=track_font,
                x=dims['display_width'] / 2 - dims['display_height'] / 2,
                y=photo_height,
                anchor='nw'
            )

            # create label for release date
            release_date_label = create_text_label(
                frame=frame,
                text=current_track['release_date'],
                bg=colors['background'],
                fg=colors['release_date'],
                text_font=release_date_font,
                x=dims['display_width'] / 2 - dims['display_height'] / 2,
                y=photo_height + track_font_height,
                anchor="nw"
            )

            # create label for artist
            artist_label = create_text_label(
                frame=frame,
                text=current_track['artist'],
                bg=colors['background'],
                fg=colors['artist'],
                text_font=artist_font,
                x=dims['display_width'] / 2 + dims['display_height'] / 2,
                y=photo_height,
                anchor='ne'
            )

            tk.update()
            track_label.destroy()
            artist_label.destroy()
            release_date_label.destroy()
            album_art_label.destroy()

        time.sleep(config['poll_interval'])


if __name__ == '__main__':
    config = get_config()
    dims = config['dimensions']
    colors = config['colors']
    fonts = config['fonts']
    display_art(create_spotify_obj())
