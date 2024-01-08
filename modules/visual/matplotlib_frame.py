import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

class MatplotlibFrame ( tk.Frame ) :
    """
    Вбудовання плоттерів matplotlib у вікно tkinter
    за допомогою полотна canvas
    """

    def __init__( self, parent, text, font) :
        tk.Frame.__init__( self, parent )
        tk.Label(self, text=" " + text + " ", font=font).pack()
        self.f = Figure( figsize = ( 100, 100 ), frameon=False )
        self.f.tight_layout()
        self.canvas = FigureCanvasTkAgg( self.f, self )
        self.canvas.get_tk_widget().pack(expand=True)
        self.canvas.figure.tight_layout()
        self.canvas.draw()
        self.plot_widget = self.canvas.get_tk_widget()
        self.toolbar = NavigationToolbar2Tk( self.canvas, self ) # підключення панелі інструментів matplotlib
        self.plot_widget.pack( side = tk.RIGHT, fill = tk.BOTH, expand = True )
        self.toolbar.update() # можливість оновлення панелі інструментів matplotlib