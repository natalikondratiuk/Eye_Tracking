class BunnyCatch:
    """
    Формування сонячних зайчиків,
    що керуються очима
    """

    def __init__(self, canvas, size, color):
        self.canvas = canvas
        self.ball = canvas.create_oval(0, 0, size, size, fill=color)
        self.pos(100, 100)

    def pos(self, cX, cY): self.canvas.move(self.ball, cX, cY)

    def get_coords(self): return self.canvas.coords(self.ball)