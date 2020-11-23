import bokeh.io
import bokeh_garden
import examples.grib_plot
import examples.grib_upload
import examples.grib_info_download

default_layout = {"widget": bokeh_garden.tabs.Tabs,
                  "Chose file": {"widget": bokeh.models.layouts.Column,
                                 "children": [{"widget": examples.grib_upload.GribUpload},
                                              {"widget": examples.grib_info_download.GribInfoDownload}]},
                  "Plot": {"widget": examples.grib_plot.GribPlot}}

class WeatherDataExplorer(bokeh_garden.application.Application):
    def __init__(self, layout = default_layout, **kw):
        bokeh_garden.application.Application.__init__(self, layout=layout, **kw)

if __name__.startswith("bokeh_app_"):
    # We got started using `bokeh serve examples/weather_data_explorer.py`
    application = WeatherDataExplorer()
    application(bokeh.plotting.curdoc())
