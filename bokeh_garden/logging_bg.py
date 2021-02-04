import bokeh.io
import bokeh_garden
import bokeh.models.sources
from bokeh.models import Div
import logging


class LoggingBG(bokeh_garden.application.AppWidget, bokeh.models.layouts.Column):
    def __init__(self, app, **kw):
        self._app = app
        handler = bokeh_garden.logging_handler.LoggingHandler(self)

        formatter = logging.Formatter(' %(asctime)s: %(levelname)s: %(name)s: %(message)s', datefmt='%H:%M:%S ')
        logger = logging.getLogger()

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        self._logtext = Div(text='', width= 400)

        self._link = bokeh_garden.download.Download(
            text="Download log",
            filename="log.txt",
            content=DownloadContent(self))

        bt = bokeh.models.widgets.Button(label='Clear log')

        self._logentry = bokeh_garden.manual_log_entry.ManualLogEntry(self)

        bokeh.models.layouts.Column.__init__(self, self._logtext, self._link, bt, self._logentry, **kw)

        bt.on_click(self.clear_log)

    def clear_log(self):
        self._records = ''
        self._logtext.text = ''


class DownloadContent(object):
    def __init__(self, widget):
        self.widget = widget

    def __bytes__(self):
        f = self.widget._records
        return f.encode("utf-8")
