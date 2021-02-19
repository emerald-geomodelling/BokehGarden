import logging
import tornado.gen
import bokeh.plotting
import weakref
import threading



class LoggingHandler(logging.Handler):
    widgets = weakref.WeakValueDictionary()
    current_document = threading.local()

    @classmethod
    def register_widget(cls, widget):
        docid = id(widget.document)
        cls.widgets[docid] = widget

    @classmethod
    def set_current_document(cls, doc):
        """Call this from a background thread to tell the thread which document / widget to log to"""
        cls.current_document.document = doc
        
    def __init__(self):
        logging.Handler.__init__(self)

    def emit_widget_coroutine(self, widget, record):
        widget.add_record(self.format(record))
        
    def emit_widget(self, widget, record):
        widget.document.add_next_tick_callback(
            tornado.gen.coroutine(
                lambda: self.emit_widget_coroutine(widget, record)))
            
    def emit(self, record):
        doc = None
        try:
            doc = self.current_document.document
        except:
            try:
                doc = bokeh.plotting.curdoc()
            except:
                pass
        if doc is None:
            for widget in self.widgets.values():
                self.emit_widget(widget, record)                
        else:
            docid = id(doc)
            if docid in self.widgets:
                self.emit_widget(self.widgets[docid], record)







