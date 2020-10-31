from io import BytesIO
from tkinter import Tk, Canvas, BOTH

import colorgram
import requests
from PIL import Image

from gui_components import TextLabel, ImageLabel


class Gui:
    def __init__(self, spotify, dims, fonts, timings, palette):
        self.root = Tk()
        self.root.configure(bg='black', cursor='none')
        self.root.attributes('-fullscreen', True)
        self.canvas = Canvas(self.root,
                             width=dims['width'],
                             height=dims['width'],
                             bg='black',
                             bd=0,
                             highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=True)

        self.album_art_label = ImageLabel(self.canvas)

        self.track_label = TextLabel(self.canvas,
                                     40,
                                     dims['width'],
                                     'sw', 0,
                                     fonts['font_family'], fonts['track'])

        self.artist_label = TextLabel(self.canvas,
                                      dims['width'],
                                      dims['width'] - 150,
                                      'ne', 270,
                                      fonts['font_family'], fonts['artist'])

        self.release_date_label = TextLabel(self.canvas,
                                            dims['width'],
                                            dims['width'] - 130,
                                            'nw', 270,
                                            fonts['font_family'], fonts['release_date'])

        self.spotify = spotify
        self.dims = dims
        self.timings = timings
        self.palette = palette
        self.current_track_name = None

    def update(self):
        try:
            current_track = self.get_current_track()

            if current_track is None:
                self.canvas.delete("all")
                self.current_track_name = None

                self.canvas.update()
                self.canvas.after(self.timings['poll_interval_sleep'] * 1000)
            elif current_track['track_name'] != self.current_track_name:
                self.canvas.delete("all")

                self.current_track_name = current_track['track_name']

                # create image
                album_art = self.get_photo_image(
                    src=current_track['album_art_uri'],
                    width=self.dims['width'],
                    height=self.dims['width']
                )

                # create thumbnail
                thumbnail = self.get_photo_image(src=current_track['thumbnail'], width=None, height=None)

                # set the image label
                self.album_art_label.show(album_art)

                # get the color palette of the image for text labels
                colors = Gui.get_image_palette(thumbnail, self.palette['count'])

                # set the text labels
                self.track_label.show(self.current_track_name, album_art, colors, self.palette['track_offset'])
                self.artist_label.show(current_track['artist'], album_art, colors, self.palette['artist_offset'])
                self.release_date_label.show(current_track['release_date'], album_art, colors,
                                             self.palette['release_date_offset'])

                self.canvas.update()
        except Exception:
            self.canvas.delete("all")
            self.canvas.update()

        self.canvas.after(self.timings['poll_interval'] * 1000, self.update)

    def get_current_track(self):
        print('spotify::get_track')
        track = self.spotify.current_user_playing_track()

        if track is None:
            return None
        artist_text = ''

        item = track['item']

        for i in range(0, len(item['artists'])):
            if i > 0:
                artist_text = artist_text + ', '

            artist_text = artist_text + item['artists'][i]['name']

        return {
            'track_name': item['name'],
            'artist': artist_text,
            'album_art_uri': item['album']['images'][0]['url'],
            'thumbnail': item['album']['images'][2]['url'],
            'release_date': item['album']['release_date'][0:7]
        }

    def mainloop(self):
        self.root.mainloop()

    @staticmethod
    def get_photo_image(src, width, height):
        res = requests.get(src)
        image = Image.open(BytesIO(res.content)).convert('RGB')
        if width is not None:
            image = image.resize((width, height), Image.ANTIALIAS)
            print('resized')
        return image

    @staticmethod
    def get_image_palette(image, count):
        colors = colorgram.extract(image, count)
        colors.sort(key=lambda c: c.rgb.r+c.rgb.g+c.rgb.b)
        return colors
