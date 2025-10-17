import sys
import bokeh.plotting

import bokeh_garden.compiler_cache

import bokeh_garden.custom_action_tool
import bokeh_garden.annotation_pan_tool
import bokeh_garden.annotation_wheel_zoom_tool
from . import serverutils
import bokeh_garden.interactive_color_bar
import bokeh_garden.upload
import bokeh_garden.download
import bokeh_garden.select
import bokeh_garden.autocomplete
import bokeh_garden.tabs
import bokeh_garden.collection
import bokeh_garden.plot_collection
import bokeh_garden.application
import bokeh_garden.progress_bar
import bokeh_garden.logging_bg
import bokeh_garden.logging_handler
import bokeh_garden.manual_log_entry

# Set default tools for bokeh-garden
import bokeh.plotting._figure
_original_figure = bokeh.plotting._figure.figure

def _patched_figure(*args, **kwargs):
    if 'tools' not in kwargs:
        kwargs['tools'] = "annotation_pan_tool,annotation_wheel_zoom_tool,box_zoom,save,reset,help"
    return _original_figure(*args, **kwargs)

bokeh.plotting.figure = _patched_figure
bokeh.plotting._figure.figure = _patched_figure
