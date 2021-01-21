import bokeh.io
import bokeh_garden
import pandas as pd
import tempfile
import pygrib
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
#formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

# file_handler = logging.FileHandler('test2.log')
# file_handler.setFormatter(formatter)

# file_handler = logging.FileHandler('sample.log')
# file_handler.setLevel(logging.ERROR)
# file_handler.setFormatter(formatter)
#logger.addHandler(file_handler)

class GribPlot(bokeh_garden.application.AppWidget, bokeh.models.layouts.Column):

    def __init__(self, app, **kw):
        self._app = app
        self._sel = bokeh_garden.select.JSONSelect()
        print("selection before")
        self._sel.on_change("value", self.sel_changed)
        print("selection after")



   #     self._test = bokeh_garden.progress_bar.ProgressBarTest(app)
   #     self._bar = bokeh_garden.progress_bar.ProgressBar(app)

        self._source = bokeh.models.ColumnDataSource(data={"images": [], "x": [], "y": [], "dw": [], "dh":[]})
        print("D source", self._source)
        self._figure = bokeh.plotting.Figure()
        print("E figure", self._figure)
        self._figure.image("images", x="x", y="y", dw="dw", dh="dh", palette="Spectral11", source=self._source)


        bokeh.models.layouts.Column.__init__(self, self._sel, self._figure, **kw)

        print("F App on change", self._app.on_change("grib", self.grib_changed))

        logger.info('GRIB PLOT')

    def grib_changed(self, attr, old, new):
        print("Grib changed")
        self._sel.json_options=[(idx, str(self._app.grib.grib.message(idx).name))
                                for idx in range(1, self._app.grib.grib.messages + 1)]
        print("grib changed done")
        logger.info('PLOT changed')

    def sel_changed(self, attr, old, new):
        print("Selection changed")
        logger.info('Selection changed')
        grb = self._app.grib.grib[self._sel.json_value]
        lats, lons = grb.latlons()
        self._source.data = bokeh.models.ColumnDataSource.from_df(pd.DataFrame({
            "images": [grb.values], "x": [lons[0,0]], "y": [lats[0,0]], "dw": [lons[-1,-1]], "dh":[lats[-1,-1]]}))

