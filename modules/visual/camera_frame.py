import tkinter as tk

class CameraFrame( tk.Frame ) :
    """
    Вбудовування вікна OpenCV у вікно Tkinter
    """

    def __init__( self, root ):
        tk.Frame.__init__( self, root, borderwidth=1, relief=tk.FLAT )
        self.labelRainbow = tk.Label( self, bg='#DCDCDC' )
        self.camLabel = tk.Label( self, bg='#BC8F8F' )
        self.labelRainbow.pack( side=tk.LEFT )
        self.camLabel.pack( side=tk.RIGHT )
        self.camLabel.forget() # приховування камери