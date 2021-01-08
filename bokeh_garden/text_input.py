import bokeh.models
from bokeh.models import TextInput
import bokeh_garden.application

class MyTextInput(bokeh_garden.application.AppWidget, bokeh.models.layouts.Row):

    def __init__(self, **kw):
        text_input = TextInput(value="default", title="Label:")

        bokeh.models.layouts.Row.__init__(self, text_input, **kw)



