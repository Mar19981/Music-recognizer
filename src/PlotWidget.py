from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class PlotWidget(FigureCanvasQTAgg):
    def __init__(self, parent = None, width: int = 5, height: int = 4, dpi: int = 100) -> None:
        figure = Figure((width, height), dpi)
        self.axes = figure.add_subplot(1,1,1)
        super(PlotWidget, self).__init__(figure)
        