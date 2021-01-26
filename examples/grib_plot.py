import bokeh.io
import bokeh_garden
import pandas as pd
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class GribPlot(bokeh_garden.application.AppWidget, bokeh.models.layouts.Column):
    def __init__(self, app, **kw):
        self._app = app
        self._sel = bokeh_garden.select.JSONSelect()
        self._sel.on_change("value", self.sel_changed)
        self._source = bokeh.models.ColumnDataSource(data={"images": [], "x": [], "y": [], "dw": [], "dh":[]})
        self._figure = bokeh.plotting.Figure()
        self._figure.image("images", x="x", y="y", dw="dw", dh="dh", palette="Spectral11", source=self._source)

        bokeh.models.layouts.Column.__init__(self, self._sel, self._figure, **kw)

        self._app.on_change("grib", self.grib_changed)

        logger.info('GRIB PLOT')

    def grib_changed(self, attr, old, new):
        self._sel.json_options=[(idx, str(self._app.grib.grib.message(idx).name))
                                for idx in range(1, self._app.grib.grib.messages + 1)]

        logger.info('PLOT changed')

    def sel_changed(self, attr, old, new):
        logger.info('Selection changed')
        grb = self._app.grib.grib[self._sel.json_value]
        lats, lons = grb.latlons()
        self._source.data = bokeh.models.ColumnDataSource.from_df(pd.DataFrame({
            "images": [grb.values], "x": [lons[0,0]], "y": [lats[0,0]], "dw": [lons[-1,-1]], "dh":[lats[-1,-1]]}))
