import logging
import tornado.gen


class LoggingHandler(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.widget = widget
        self.widget._records = ''

    def update_wrapper(self):
        self.widget._logtext.text = "<pre>%s</pre>" % self.widget._records
        self.widget._link.content.encode = self.widget._records

    def emit(self, record):
        self.format(record)
        self.widget._records += self.format(record) + "\n"
        self.widget.document.add_next_tick_callback(tornado.gen.coroutine(self.update_wrapper))








