import bokeh.models

class AutocompleteInput(bokeh.models.AutocompleteInput):
    """Bugfixed AutocompleteInput that works both for typed and drop-down
    selected values. To get the current value, use self.value_input
    instead of self.value
    """

    __view_model__ = bokeh.models.AutocompleteInput.__view_model__
    __view_module__ = bokeh.models.AutocompleteInput.__view_module__
    __subtype__ = "BokehGardenAutocompleteInput"

    def __init__(self, *arg, **kw):
        bokeh.models.AutocompleteInput.__init__(self, *arg, **kw)
        self.on_change("value", self._fix_value)
    
    def _fix_value(self, attr, old, new):
        self.value_input = self.value
