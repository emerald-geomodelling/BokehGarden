import sys
import bokeh.plotting

import bokeh_garden.annotation_pan_tool
import bokeh_garden.annotation_wheel_zoom_tool
import bokeh_garden.interactive_color_bar


sys.modules["bokeh.plotting.figure"].FigureOptions.tools.property._default = "annotation_pan_tool,annotation_wheel_zoom_tool,box_zoom,save,reset,help"
