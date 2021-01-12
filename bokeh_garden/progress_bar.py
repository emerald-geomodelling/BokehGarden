import bokeh.models
import bokeh.models
from bokeh.models import TextInput
import bokeh_garden.application
from bokeh.io import curdoc, show
from bokeh.models import ColumnDataSource, Grid, LinearAxis, Plot, Quad
from bokeh.models import Button
from bokeh.io import curdoc
from bokeh.models import Range1d


# from bokeh.plotting import figure


class ProgressBar(bokeh_garden.application.AppWidget, bokeh.plotting.Figure):
    def __init__(self, app, **kw):
        self._app = app
        self._current_value = 0
        self._plot_width = 400
        self._success = True
        data = {'x_values': [0]}


        self._source = ColumnDataSource(data=data)


        fig = bokeh.plotting.Figure.__init__(self,
                                             plot_width=self._plot_width, plot_height=50,
                                             **kw)
        self.x_range = Range1d(0, 100, bounds=(0, 100))
        self.y_range = Range1d(0, 1, bounds=(0, 1))
        self._bar = self.hbar(y=0.5, right="x_values", height=2, left=0, color="#00779B", source=self._source, level="underlay")
        self.grid.grid_line_color = None
        self.toolbar_location = None
        self.yaxis.visible = False
        self._text = self.text(x=50, y=0, text=[''], level="overlay")

    def reset(self):
        self._current_value = 0
        self._bar.glyph.line_color = "#00779B"
        self._bar.glyph.fill_color = "#00779B"
        self._source.data['x_values'] = [self._current_value]

    def set(self, value, status=None):
        self._current_value = value
        self._source.data['x_values'] = [self._current_value]
        if status is not None:
            self._text.glyph.text = [status]

        if value == 100:
            self._bar.glyph.line_color = "#009B77"
            self._bar.glyph.fill_color = "#009B77"
            
    def get(self):
        return self._current_value

    def fail(self):
        self._success = False
        self._bar.glyph.line_color = "#9B3333"
        self._bar.glyph.fill_color = "#9B3333"
        if self._current_value < 10:
            self._current_value = 50
            self._source.data['x_values'] = [self._current_value]
        return self._success

class ProgressBars(bokeh_garden.application.AppWidget, bokeh.models.layouts.Column):
    def __init__(self, app, **kw):
        self._app = app
        bokeh.layouts.Column.__init__(self, sizing_mode="scale_both", **kw)

    def add_bar(self):
        self._new_bar = ProgressBar(self._app)
        self.check_bar()
        self.children.append(self._new_bar)
        return self._new_bar

    def check_bar(self):
        old_bars = []
        for idx in self.children:
            if idx._current_value >= 100 or idx._success == False:
                old_bars.append(idx)
                self.remove_bar(idx)

    def remove_bar(self, bar):
        self.children.index(bar)
        self.children.pop()

