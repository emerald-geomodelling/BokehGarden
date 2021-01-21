import bokeh.io
import bokeh_garden
import examples.grib_plot
import examples.grib_upload
import examples.grib_info_download
import logging
import examples.grib_log

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

#file_handler = logging.FileHandler('test2.log')
#file_handler.setFormatter(formatter)
#
# file_handler = logging.FileHandler('sample.log')
# file_handler.setLevel(logging.ERROR)
# file_handler.setFormatter(formatter)
#logger.addHandler(file_handler)

default_layout = {"widget": bokeh_garden.tabs.Tabs,
                  "Chose file": {"widget": bokeh.models.layouts.Column,
                                 "children": [{"widget": examples.grib_upload.GribUpload},
                                              {"widget": examples.grib_info_download.GribInfoDownload}]},
                  "Plot": {"widget": examples.grib_plot.GribPlot},
                  "Log": {"widget": examples.grib_log.GribLog}}

class WeatherDataExplorer(bokeh_garden.application.Application):
    def __init__(self, layout = default_layout, **kw):
        bokeh_garden.application.Application.__init__(self, layout=layout, **kw)
        logger.info('Weather Data Explorer')

if __name__.startswith("bokeh_app_"):
    # We got started using `bokeh serve examples/weather_data_explorer.py`
    application = WeatherDataExplorer()
    application(bokeh.plotting.curdoc())
