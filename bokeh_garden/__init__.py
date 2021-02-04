import sys
import bokeh.plotting

import bokeh_garden.compiler_cache

import bokeh_garden.annotation_pan_tool
import bokeh_garden.annotation_wheel_zoom_tool
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

sys.modules["bokeh.plotting.figure"].FigureOptions.tools.property._default = "annotation_pan_tool,annotation_wheel_zoom_tool,box_zoom,save,reset,help"
