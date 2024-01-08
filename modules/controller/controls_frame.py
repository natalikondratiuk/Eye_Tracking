class ControlFrame :
    """
    Формування банерів
    для вибору користувацьких налаштувань
    """

    def __init__(self, canvas, x, y, text:str, width=400, height=100, bg_color='azure1', frame_disabled='red', thickness=5):
        self.canvas = canvas
        self.banner = self.canvas.create_rectangle(x, y, x+width, y+height, fill=bg_color, outline=frame_disabled, width=thickness)
        self.text = self.canvas.create_text(x+width/2, y+height/2, text=text, fill='black', font=('Helvetica 25 bold'))

    def make_active(self, bg_color:str=None, frame_active='green') :
        self.canvas.itemconfig(self.banner, outline=frame_active)
        if isinstance(bg_color, str) :
            self.canvas.configure(bg=bg_color)

    def make_disabled(self, frame_disabled='red') :
        self.canvas.itemconfig(self.banner, outline=frame_disabled)

    def get_pos(self) : return self.canvas.coords(self.banner)

    def check_pos(self, cX, cY) :
        return cX > self.get_pos()[0] and cY > self.get_pos()[1]\
               and cX < self.get_pos()[2] and cY < self.get_pos()[3]