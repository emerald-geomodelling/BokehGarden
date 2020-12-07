import bokeh.themes
import importlib

from . import collection

def load_cls(name):
    modname, clsname = name.rsplit(".", 1)
    return getattr(importlib.import_module(modname), clsname)

class PlotCollection(collection.Collection):
    def __init__(self, doc, layout = {}, overlays = []):
        self._doc = doc
        self._layout_template = layout
        self._overlays_template = overlays
        self._layout = None
        self._overlays = []
        collection.Collection.__init__(self)
        self.generate_plots()

    @property
    def doc(self):
        return self._doc
        
    def instantiate(self, template, overlays=False):
        if isinstance(template, (list, tuple)):
            return [self.instantiate(item) for item in template]
        elif isinstance(template, dict):
            t = dict(template)
            if "widget" in t:
                w = t.pop("widget")
                if isinstance(w, str):
                    w = load_cls(w)
                if hasattr(w, "appwidget") or overlays:
                    return w(self, **self.instantiate(t))
                else:
                    return w(**self.instantiate(t))
            else:
                return {name: self.instantiate(value) for name, value in template.items()}
        else:
            return template

    def generate_plots(self):
        self._layout = self.instantiate(self._layout_template)
        self._doc.add_root(self._layout)
        self._overlays = self.instantiate(self._overlays_template, overlays=True)
