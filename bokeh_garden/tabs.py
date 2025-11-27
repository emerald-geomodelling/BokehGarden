import bokeh.models
import bokeh.models.layouts

class Tabs(bokeh.models.Tabs):
    __view_model__ = bokeh.models.Tabs.__view_model__
    __view_module__ = bokeh.models.Tabs.__view_module__
    __subtype__ = 'BokehGardenTabs'
    def __init__(self, **kw):
        bokeh.models.Tabs.__init__(self, **{name: item for name, item in kw.items()
                                                    if not isinstance(item, bokeh.models.layouts.LayoutDOM)})
        self.tabs = [bokeh.models.TabPanel(child=item, title=name)
                     for name, item in kw.items() if isinstance(item, bokeh.models.layouts.LayoutDOM)]
