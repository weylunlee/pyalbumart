"""
This gui module has all things pertaining
to the graphical user interface
"""
from io import BytesIO
from tkinter import Tk, Canvas, BOTH

import colorgram
import requests
from PIL import Image
from PIL import ImageTk


class Gui:
    """Main GUI class - also defines provisions for main loop"""
    # pylint: disable=too-many-instance-attributes
    # Nine is reasonable in this case.
    def __init__(self, spotify, config):
        self.root = Tk()
        self.root.configure(bg='black', cursor='none')
        self.root.attributes('-fullscreen', True)
        self.canvas = Canvas(self.root,
                             width=config.dimensions.width,
                             height=config.dimensions.width,
                             bg='black',
                             bd=0,
                             highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=True)

        self.album_art_label = ImageLabel(self.canvas)

        self.track_label = TextLabel(self.canvas,
                                     40,
                                     config.dimensions.width,
                                     'sw', 0,
                                     config.fonts.font_family,
                                     config.fonts.track)

        self.artist_label = TextLabel(self.canvas,
                                      config.dimensions.width,
                                      config.dimensions.width - 150,
                                      'ne', 270,
                                      config.fonts.font_family,
                                      config.fonts.artist)

        self.date_label = TextLabel(self.canvas,
                                    config.dimensions.width,
                                    config.dimensions.width - 130,
                                    'nw', 270,
                                    config.fonts.font_family,
                                    config.fonts.release_date)

        self.spotify = spotify
        self.config = config
        self.current_track_name = None

    def update(self):
        """Main loop method which updates the screen if necessary based on whether
        new track is playing since last update"""
        try:
            current_track = self.get_current_track()

            if current_track is None:
                self.canvas.delete("all")
                self.current_track_name = None

                self.canvas.update()
                self.canvas.after(self.config.timings.poll_interval_sleep * 1000)
            elif current_track['track_name'] != self.current_track_name:
                self.canvas.delete("all")

                self.current_track_name = current_track['track_name']

                # create image
                album_art = self.get_photo_image(
                    src=current_track['album_art_uri'],
                    width=self.config.dimensions.width,
                    height=self.config.dimensions.width)

                # create thumbnail
                thumbnail = self.get_photo_image(
                    src=current_track['thumbnail'], width=None, height=None)

                # set the image label
                self.album_art_label.show(album_art)

                # get the color palette of the image for text labels
                colors = Gui.get_image_palette(thumbnail, self.config.palette.count)

                # set the text labels
                self.track_label.show(self.current_track_name, album_art, colors,
                                      self.config.palette.track_offset)
                self.artist_label.show(current_track['artist'], album_art, colors,
                                       self.config.palette.artist_offset)
                self.date_label.show(current_track['release_date'], album_art, colors,
                                     self.config.palette.release_date_offset)

                self.canvas.update()
        except Exception:
            self.canvas.delete("all")
            self.canvas.update()

        self.canvas.after(self.config.timings.poll_interval * 1000, self.update)

    def get_current_track(self):
        """Returns the current playing track information"""
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
        """Exposes mainloop method so that can be called by GUI client"""
        self.root.mainloop()

    @staticmethod
    def get_photo_image(src, width, height):
        """Opens image given by URL and resizes to width x height if given"""
        res = requests.get(src)
        image = Image.open(BytesIO(res.content)).convert('RGB')
        if width is not None:
            image = image.resize((width, height), Image.ANTIALIAS)
            print('resized')
        return image

    @staticmethod
    def get_image_palette(image, count):
        """Returns an array of size count of the colors used in the image sorted by darkest first"""
        colors = colorgram.extract(image, count)
        colors.sort(key=lambda c: c.rgb.r+c.rgb.g+c.rgb.b)
        for color in colors:
            print(color.rgb)

        return colors


# Class responsible for displaying text labels on the canvas
class TextLabel:
    """A text label component"""
    def __init__(self, canvas, x, y, anchor, angle, font_family, font_size):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.anchor = anchor
        self.angle = angle
        self.font_family = font_family
        self.font_size = font_size

    def show(self, text, image, colors, palette_offset):
        """"Show a label given text and other attributes"""
        is_color_bright = TextLabel.is_color_bright(
            image, self.x, self.y)

        self.canvas.create_text(
            self.x+1,
            self.y+1,
            text=text,
            fill='#ffffff' if is_color_bright else '#000000',
            font=(self.font_family, self.font_size),
            anchor=self.anchor,
            angle=self.angle
        )

        rgb = colors[0+palette_offset] if is_color_bright else colors[len(colors)-1-palette_offset]
        color_hex = '#%02x%02x%02x' % (rgb.rgb.r, rgb.rgb.g, rgb.rgb .b)

        self.canvas.create_text(
            self.x,
            self.y,
            text=text,
            fill=color_hex,
            font=(self.font_family, self.font_size),
            anchor=self.anchor,
            angle=self.angle
        )

    @staticmethod
    def is_color_bright(image, x, y):
        """"Returns if color at specified location of image is a bright color"""
        try:
            r, g, b = image.getpixel((x, y))
            return (r + g + b) / 3 > 175
        except Exception:
            return False


# Class responsible for displaying image labels on the screen
class ImageLabel:
    """An image label component"""
    def __init__(self, canvas):
        self.canvas = canvas
        self.prev_image = None
        self.tk_image = None

    def show(self, image):
        """Shows the specified image"""
        # if prev image exists, fade to new image
        if self.prev_image is not None:
            alpha = 0
            while alpha < 1.0:
                new_img = Image.blend(self.prev_image, image, alpha)
                alpha += 0.02
                tk_image = ImageTk.PhotoImage(new_img)
                self.canvas.create_image(0, 0, image=tk_image, anchor='nw')
                self.canvas.update()

        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.tk_image, anchor='nw')
        self.prev_image = image
