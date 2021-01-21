import bokeh.io
import bokeh_garden
import pandas as pd
import tempfile
import pygrib
import io
import bokeh.models.sources
#from bokeh.io import show
from bokeh.models import Div
from bokeh.models import CustomJS, TextInput
import examples.grib_log
import logging



class GribLog(bokeh_garden.application.AppWidget, bokeh.models.layouts.Column):
    def __init__(self, app, **kw):
        self._app = app
        handler = examples.bokeh_handler.BokehHandler(self)

        formatter = logging.Formatter(' %(asctime)s: %(levelname)s: %(name)s: %(message)s', datefmt='%H:%M:%S ')
        logger= logging.getLogger()

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        self._logtext = Div(text='', width= 400)

        self._link = bokeh_garden.download.Download(
            text="Download log",
            filename="log.txt",
            content=DownloadContent(self))

        bt = bokeh.models.widgets.Button(label='Clear log')

        bokeh.models.layouts.Column.__init__(self, self._logtext, self._link, bt, **kw)

        bt.on_click(self.clear_log)

    def clear_log(self):
        self._logtext.text = ''
        self._records = ''

class DownloadContent(object):

    def __init__(self, widget):
        self.widget = widget

    def __bytes__(self):
        print("bytes", self.widget._link.content)
        f = self.widget._records
        print('F', f)
     #   return self.widget._logtext.text.encode("utf-8")
        return f.encode("utf-8")






