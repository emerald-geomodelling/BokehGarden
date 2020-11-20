import weakref

from . import plot_collection

class Application(object):
    PlotCollection = plot_collection.PlotCollection
    
    def __init__(self, layout = {}, overlays = [], **kw):
        self.layout_template = layout
        self.overlays_template = overlays
        self.kw = kw
        self.docs = weakref.WeakKeyDictionary()

    def __call__(self, doc):
        self.docs[doc] = self.PlotCollection(doc, self.layout_template, self.overlays_template, **self.kw)

    @property
    def doc(self):
        return next(self.docs.keys())
    
    @property
    def plot(self):
        return next(self.docs.values())

    @property
    def layout(self):
        return self.plot._layout

    @property
    def overlays(self):
        return self.plot._overlays
