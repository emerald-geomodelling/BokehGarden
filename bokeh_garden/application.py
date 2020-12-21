import weakref
import bokeh.model
import bokeh.core.properties

from . import plot_collection

MetaModel = type(bokeh.model.Model)

class MetaAppWidget(MetaModel):
    def __new__(cls, name, bases, attr):
        css = "%s.%s" % (attr["__module__"], name)
        css = css.lower().replace(".", "-").replace("_", "-")
        attr["css_classes"] = bokeh.core.properties.Override(default=[css])
        return super(MetaAppWidget, cls).__new__(cls, name, bases, attr)
        
class AppWidget(bokeh.model.Model):
    appwidget = True
    @classmethod
    def __init_subclass__(cls):
        cls.__view_model__ = cls.__bases__[-1].__view_model__
        cls.__view_module__ = cls.__bases__[-1].__view_module__
        cls.__subtype__ = cls.__name__
        css = "%s.%s" % (cls.__module__, cls.__name__)
        cls._css_name = css.lower().replace(".", "-").replace("_", "-")
        super(AppWidget, cls).__init_subclass__()

    def properties_with_values(self, include_defaults):
        if self._css_name not in self.css_classes:
            self.css_classes.append(self._css_name)
        return super(AppWidget, self).properties_with_values(include_defaults)
        
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
