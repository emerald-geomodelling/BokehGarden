import bokeh.models
import json

def npencode(obj):
    if hasattr(obj, "dtype"):
        return obj.item()
    raise ValueError

class JSONSelect(bokeh.models.Select):
    __view_model__ = bokeh.models.Select.__view_model__
    __view_module__ = bokeh.models.Select.__view_module__
    __subtype__ = "JSONSelect"

    def __init__(self, json_options=None, json_value=None, *arg, **kw):
        bokeh.models.Select.__init__(self, *arg, **kw)
        if json_options is not None:
            self.json_options = json_options
        if json_value is not None:
            self.json_value = json_value
    
    @property
    def json_options(self):
        if not self.options: return self.options
        return [(json.loads(value), label) for (value, label) in self.options]
    
    @json_options.setter
    def json_options(self, options):
        if isinstance(options, dict):
            options = list(options.items())
            options.sort(key=lambda a: str(a[1])) # Sort by label
        self.options = [(json.dumps(value, default=npencode, sort_keys=True), str(label)) for (value, label) in options]
        if self.options and (self.value is None or self.value not in [option[0] for option in self.options]):
            self.value = [option[0] for option in self.options][0]

    @property
    def json_value(self):
        if not self.value: return self.value
        return json.loads(self.value)

    @json_value.setter
    def json_value(self, value):
        self.value = json.dumps(value, default=npencode, sort_keys=True)
