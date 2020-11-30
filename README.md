# BokehGarden

BokehGarden is a [Bokeh](https://bokeh.org/) based web application
framework focused on plotting heavy interactive applications.

Additionally, it provides several improved widgets for Bokeh, that can
be used both within the framework and in a standalone bokeh app:

* Interactive colorbar
  - That allows adjusting the color map by pan and zoom
* File download button
  - That goes directly over http (not websocket)
* File upload field
  - That goes directly over http (not websocket), meaning that it does
    not have a size limit, nor does it encode the file as base64.
* Autocomplete input field
  - That fixes the text entry vs drop down selection problem
* Drop down menu
  - That encodes the entry id:s as json, allowing e.g. integers to be
    used as id:s, not just strings.

## Example application

    bokeh serve examples/weather_data_explorer.py

## Framework usage

The BokehGarden application framework consists of a very old idea,
applied to Bokeh, combined with a small tool. The simple idea is to
create complex UI element from simpler ones by subclassing Bokeh
widget classes. In the subclass, the `__init__()` method is used to
populate the widget with parts and bind callbacks.

    class MyForm(bokeh_garden.application.AppWidget, bokeh.layouts.Column):
        def __init__(self, app=None, **kw):
            self._app = app

            self._foo = bokeh.models.Slider(title="Select a value for foo", value=0, start=0, end=100, step=1)
            self._bar = bokeh.models.NumericInput(title="Bar value", mode="float", value=10)
            self._submit_button = bokeh.models.Button(label="Submit", button_type="primary")
            self._submit_button.on_event(bokeh.events.ButtonClick, self.on_submit)
            
            bokeh.layouts.Column.__init__(
              self, self._foo, self._bar, self._submit_button, **kw)

        def on_submit(self, event):
            print("Submitted values:", self._foo.value, self._bar.value)

The above widget could be used as any other Bokeh widget in your
plots.

Additionally, it could be used inside another widget of the same type,
to recursively build up complex interfaces. But there is a better way:
Layouts and overlays.

### Layouts

A layout is a simple dictionary based data structure that defines the
layout of an application declaratively. It is equivalent to
instantiating widgets, sending them as parameters when instantiating
other widgets to gradually build up the application layout, just like
you normally do in bokeh. However, since it's data, not code, it's
easy to store and modify the structure. Example:

    layout = {"widget": bokeh_garden.tabs.Tabs,
              "Data": {"widget": DataLoaderForm},
              "Sea": {"widget": bokeh.models.layouts.Column,
                      "children": [{"widget": WavesPlot, "unit": "kn"},
                                   {"widget": CurentsPlot, "unit": "kn"}]},
              "Air": {"widget": bokeh.models.layouts.Row,
                      "children": [{"widget": PressurePlot, "tags": ["wind_map"]},
                                   {"widget": WindPlot, "tags": ["wind_map"]}]}}
                                   
At each level, it consists of a dictionary with the key `widget`
holding a widget class, and other keys being used to generate the
parameters to `__init__()` for that class. `__init__()` will also receive an instance of
`bokeh_garden.application.Application` as a first argument. This instance is shared among all
widgets created using the layout. The layout above would translate into


    layout_instance = bokeh_garden.tabs.Tabs(
        app,
        Data=DataLoaderForm(app),
        Sea=bokeh.models.layouts.Column(
            *[WavesPlot(app, unit="kn"),
              CurentsPlot(app, unit="kn")]),
        Air=bokeh.models.layouts.Row(
            *[PressurePlot(app, tags=["wind_map"]),
              WindPlot(app, tags=["wind_map"])]))

### Overlays

The layout structure above lets you build complex applications from
highly independent widgets. But it has one drawback: What if you need
to make widgets in different parts of the application interact?
Overlays solve this problem.

Overlays are ordinary python classes that has access to the document
and the widget tree, can query the widget tree and modify the widgets
in it by e.g. binding callbacks or adding drawing operations (layers)
to plots.

    class WindMapLinkedMapExtentsOverlay(object):
        def __init__(self, app):
            self.app = app

            x_range = None
            y_range = None
            for figure in self.app.doc.select({"tags": ["wind_map"]}):
                if x_range is None:
                    x_range = figure.x_range
                    y_range = figure.y_range
                else:
                    figure.x_range = x_range
                    figure.y_range = y_range

    overlays = [{"widget": WindMapLinkedMapExtentsOverlay},
                ...]

### Instantiating your layout

Once you have built a layout and defined your overlays, you can
instantiate them as a Bokeh application using the following code
(notebook version):

    bokeh.io.output_notebook()
    application = bokeh_garden.application.Application(layout, overlays)
    bokeh.io.show(application)

or (application file for bokeh serve):

    application = bokeh_garden.application.Application(layout, overlays)
    application(bokeh.plotting.curdoc())
