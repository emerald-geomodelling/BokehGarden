import bokeh.models.widgets
import bokeh.models.layouts

class Tabs(bokeh.models.widgets.Tabs):
    __view_model__ = bokeh.models.widgets.Tabs.__view_model__
    __view_module__ = bokeh.models.widgets.Tabs.__view_module__
    __subtype__ = 'BokehGardenTabs'
    def __init__(self, **kw):
        bokeh.models.widgets.Tabs.__init__(self, **{name: item for name, item in kw.items()
                                                    if not isinstance(item, bokeh.models.layouts.LayoutDOM)})
        self.tabs = [bokeh.models.widgets.Panel(child=item, title=name)
                     for name, item in kw.items() if isinstance(item, bokeh.models.layouts.LayoutDOM)]
