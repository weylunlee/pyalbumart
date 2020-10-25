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

    def show(self, text, image):
        self.canvas.create_text(
            self.x,
            self.y,
            text=text,
            fill='#ffffff',
            font=(self.font_family, self.font_size),
            anchor=self.anchor,
            angle=self.angle
        )


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
                alpha += 0.01
                tk_image = ImageTk.PhotoImage(new_img)
                self.canvas.create_image(0, 0, image=tk_image, anchor='nw')
                self.canvas.update()

        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.tk_image, anchor='nw')
        self.prev_image = image
