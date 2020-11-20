import bokeh.model
import bokeh.core.properties
import bokeh.util.callback_manager

class Collection(bokeh.model.Model):
    objects = bokeh.core.properties.Dict(bokeh.core.properties.String, bokeh.core.properties.Instance(bokeh.model.Model))
    def on_change(self, attr, *callbacks):
        bokeh.util.callback_manager.PropertyCallbackManager.on_change(self, attr, *callbacks)
    def __setattr__(self, name, value):
        if name.startswith("_"):
            bokeh.model.Model.__setattr__(self, name, value)
        else:
            old = self.objects.get(name, None)
            self.objects[name] = value
            self.trigger(name, old, value)
    def __getattr__(self, name):
        if name.startswith("_"):
            return super(Collection, self).__getattribute__(name)
        return super(Collection, self).__getattribute__("objects")[name]
