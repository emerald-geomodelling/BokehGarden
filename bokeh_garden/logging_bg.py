import bokeh.io
import bokeh_garden
import bokeh.models.sources
from bokeh.models import Div
import logging



class LoggingBG(bokeh_garden.application.AppWidget, bokeh.models.layouts.Column):
    def __init__(self, app, **kw):
        self._app = app

        self._records = ''
        self._queue = []
        self._logtext = Div(text='', style={"overflow": "auto", "width": "100%"}, **kw)

        self._link = bokeh_garden.download.Download(
            text="Download log",
            filename="log.txt",
            content=DownloadContent(self))

        bt = bokeh.models.widgets.Button(label='Clear log')

        bokeh.models.layouts.Column.__init__(self, self._logtext, self._link, bt, **kw)

        bt.on_click(self.clear_log)

    def _attach_document(self, doc):
        res = super(LoggingBG, self)._attach_document(doc)
        bokeh_garden.logging_handler.LoggingHandler.register_widget(self)
        doc.add_periodic_callback(lambda : self._handle_queue(), 500)
        return res

    def _handle_queue(self):
        queue = self._queue
        self._queue = []
        if queue:
            self._records = self._records + "\n".join(queue) + "\n"
            self._logtext.text = "<pre>%s</pre>" % self._records
        
    def add_record(self, record):
        self._queue.append(record)
    
    def clear_log(self):
        self._records = ''
        self._logtext.text = ''

class DownloadContent(object):
    def __init__(self, widget):
        self.widget = widget

    def __bytes__(self):
        f = self.widget._records
        return f.encode("utf-8")
