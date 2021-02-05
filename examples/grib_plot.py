import bokeh.io
import bokeh_garden
import pandas as pd
import logging
import bokeh_garden.custom_action_tool
import bokeh.events

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class GribPlot(bokeh_garden.application.AppWidget, bokeh.models.layouts.Column):
    def __init__(self, app, **kw):
        self._app = app
        self._sel = bokeh_garden.select.JSONSelect()
        self._sel.on_change("value", self.sel_changed)
        self._source = bokeh.models.ColumnDataSource(data={"images": [], "x": [], "y": [], "dw": [], "dh":[]})
        self._figure = bokeh.plotting.Figure(tools="pan,wheel_zoom,box_zoom")
        self._figure.image("images", x="x", y="y", dw="dw", dh="dh", palette="Spectral11", source=self._source)

        tool = bokeh_garden.custom_action_tool.CustomActionTool(
            icon = 'data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgZm9jdXNhYmxlPSJmYWxzZSIgZGF0YS1wcmVmaXg9ImZhciIgZGF0YS1pY29uPSJzbWlsZSIgY2xhc3M9InN2Zy1pbmxpbmUtLWZhIGZhLXNtaWxlIGZhLXctMTYiIHJvbGU9ImltZyIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB2aWV3Qm94PSIwIDAgNDk2IDUxMiI+PHBhdGggZmlsbD0iY3VycmVudENvbG9yIiBkPSJNMjQ4IDhDMTExIDggMCAxMTkgMCAyNTZzMTExIDI0OCAyNDggMjQ4IDI0OC0xMTEgMjQ4LTI0OFMzODUgOCAyNDggOHptMCA0NDhjLTExMC4zIDAtMjAwLTg5LjctMjAwLTIwMFMxMzcuNyA1NiAyNDggNTZzMjAwIDg5LjcgMjAwIDIwMC04OS43IDIwMC0yMDAgMjAwem0tODAtMjE2YzE3LjcgMCAzMi0xNC4zIDMyLTMycy0xNC4zLTMyLTMyLTMyLTMyIDE0LjMtMzIgMzIgMTQuMyAzMiAzMiAzMnptMTYwIDBjMTcuNyAwIDMyLTE0LjMgMzItMzJzLTE0LjMtMzItMzItMzItMzIgMTQuMy0zMiAzMiAxNC4zIDMyIDMyIDMyem00IDcyLjZjLTIwLjggMjUtNTEuNSAzOS40LTg0IDM5LjRzLTYzLjItMTQuMy04NC0zOS40Yy04LjUtMTAuMi0yMy43LTExLjUtMzMuOC0zLjEtMTAuMiA4LjUtMTEuNSAyMy42LTMuMSAzMy44IDMwIDM2IDc0LjEgNTYuNiAxMjAuOSA1Ni42czkwLjktMjAuNiAxMjAuOS01Ni42YzguNS0xMC4yIDcuMS0yNS4zLTMuMS0zMy44LTEwLjEtOC40LTI1LjMtNy4xLTMzLjggMy4xeiI+PC9wYXRoPjwvc3ZnPg==',
            tool_name='A custom tool button')
        self._figure.add_tools(tool)
        def callback(event):
            print("The custom tool button got clicked!")
        tool.on_event(bokeh.events.ButtonClick, callback)
        
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
