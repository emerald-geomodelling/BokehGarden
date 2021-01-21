import logging
import requests
import examples.grib_log

class BokehHandler(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.widget = widget
        self.widget._records = ''
    def emit(self, record):
        self.widget

        self.format(record)

        self.widget._records += self.format(record) + "\n"
        self.widget._logtext.text = "<pre>%s</pre>" % self.widget._records
        self.widget._link.content.encode = self.widget._records
     #   print('emit', self.widget._link.content.encode)







