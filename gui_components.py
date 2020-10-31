from PIL import Image, ImageTk


# Class responsible for displaying text labels on the canvas
class TextLabel:
    def __init__(self, canvas, x, y, anchor, angle, font_family, font_size):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.anchor = anchor
        self.angle = angle
        self.font_family = font_family
        self.font_size = font_size

    def show(self, text, image, colors, palette_offset):
        sample_x_offset = -5 if self.anchor[1:2] == 'w' else -5
        sample_y_offset = -5 if self.anchor[0:1] == 'n' else -5

        is_color_bright = TextLabel.is_color_bright(image, self.x + sample_x_offset, self.y + sample_y_offset)

        self.canvas.create_text(
            self.x+1,
            self.y+1,
            text=text,
            fill='#ffffff' if is_color_bright else '#000000',
            font=(self.font_family, self.font_size, 'bold'),
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
            font=(self.font_family, self.font_size, 'bold'),
            anchor=self.anchor,
            angle=self.angle
        )

    @staticmethod
    def is_color_bright(image, x, y):
        try:
            r, g, b = image.getpixel((x, y))
            return (r + g + b) / 3 > 175
        except Exception:
            return False


# Class responsible for displaying image labels on the screen
class ImageLabel:
    def __init__(self, canvas):
        self.canvas = canvas
        self.prev_image = None
        self.tk_image = None

    def show(self, image):
        # if prev image exists, fade to new image
        if self.prev_image is not None:
            alpha = 0
            while 1.0 > alpha:
                new_img = Image.blend(self.prev_image, image, alpha)
                alpha += 0.02
                tk_image = ImageTk.PhotoImage(new_img)
                self.canvas.create_image(0, 0, image=tk_image, anchor='nw')
                self.canvas.update()

        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.tk_image, anchor='nw')
        self.prev_image = image
