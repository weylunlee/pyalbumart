from io import BytesIO
from tkinter import Tk, Canvas, BOTH

import requests
from PIL import Image

from gui_components import TextLabel, ImageLabel


class Gui:
    def __init__(self, spotify, dims, fonts, timings):
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
                                      fonts['font_family'], fonts['track'])

        self.release_date_label = TextLabel(self.canvas,
                                            dims['width'],
                                            dims['width'] - 130,
                                            'nw', 270,
                                            fonts['font_family'], fonts['track'])

        self.spotify = spotify
        self.dims = dims
        self.timings = timings
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

                # set the image label
                self.album_art_label.show(album_art)

                # set the text labels
                self.track_label.show(self.current_track_name, None)
                self.artist_label.show(current_track['artist'], None)
                self.release_date_label.show(current_track['release_date'], None)

                self.canvas.update()
        except Exception:
            self.canvas.delete("all")
            self.canvas.update()

        self.canvas.after(self.timings['poll_interval'] * 1000, self.update)

    def get_current_track(self):
        print('spotify::get_track')
        track = self.spotify.current_user_playing_track()

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

    def mainloop(self):
        self.root.mainloop()

    @staticmethod
    def is_color_bright(image_obj, x, y):
        try:
            r, g, b = image_obj.getpixel((x, y))
            return (r + g + b) / 3 > 127
        except Exception:
            return False

    @staticmethod
    def get_photo_image(src, width, height):
        res = requests.get(src)
        image = Image.open(BytesIO(res.content)).resize((width, height), Image.ANTIALIAS).convert('RGB')
        return image
