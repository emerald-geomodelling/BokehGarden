# BokehGarden/tests/mini_app_advanced.py
"""
Mini Plot Application - Using bokeh_garden AnnotationWheelZoomTool
"""
import numpy as np
import pandas as pd
import io
import traceback

# Import Bokeh components FIRST
from bokeh.layouts import column, row
from bokeh.models import Button, Div
from bokeh.plotting import figure, curdoc

# Import from bokeh_garden
import sys
import os

bokeh_garden_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if bokeh_garden_path not in sys.path:
	sys.path.insert(0, bokeh_garden_path)

print("[IMPORT] About to import AnnotationWheelZoomTool from bokeh_garden")
from bokeh_garden.annotation_wheel_zoom_tool import AnnotationWheelZoomTool

print("[IMPORT] AnnotationWheelZoomTool imported successfully")


class MiniPlotApp:
	"""Mini application using bokeh_garden AnnotationWheelZoomTool"""

	def __init__(self, doc):
		print("[INIT] MiniPlotApp.__init__ called")

		try:
			self.doc = doc
			self.data_source = self.generate_default_data()
			print(f"[INIT] Generated {len(self.data_source)} data points")

			# Build UI components
			self.setup_plot()
			print("[INIT] Plot created")

			self.setup_widgets()
			print("[INIT] Widgets created")

			self.setup_layout()
			print("[INIT] Layout added to document")

		except Exception as e:
			print(f"[ERROR] Exception in __init__: {e}")
			traceback.print_exc()
			raise

	def generate_default_data(self):
		"""Generate default sine wave data"""
		x = np.linspace(0, 4 * np.pi, 100)
		y = np.sin(x)
		return pd.DataFrame({'x': x, 'y': y})

	def setup_plot(self):
		"""Create the main plot figure with custom tool"""
		# Create custom annotation wheel zoom tool
		annotation_zoom = AnnotationWheelZoomTool()

		self.figure = figure(
			width=800,
			height=400,
			title="Data Visualization with AnnotationWheelZoomTool",
			x_axis_label='X Axis',
			y_axis_label='Y Axis',
			toolbar_location="above",
			tools=[
				"pan",
				annotation_zoom,  # Use the custom tool
				"box_zoom",
				"reset",
				"save"
			],
			active_scroll=annotation_zoom,  # Make it the active scroll tool
			background_fill_color="#fafafa"
		)

		# Plot the line
		self.line_renderer = self.figure.line(
			self.data_source['x'],
			self.data_source['y'],
			line_width=3,
			color='#2E86AB',
			alpha=0.8,
			legend_label='Data Series'
		)

		# Add circles
		self.circle_renderer = self.figure.scatter(
			self.data_source['x'],
			self.data_source['y'],
			size=6,
			color='#A23B72',
			alpha=0.6,
			legend_label='Data Points'
		)

		self.figure.legend.click_policy = "hide"

	def setup_widgets(self):
		"""Create control widgets"""
		print("[WIDGETS] Creating widgets")

		self.title_div = Div(
			text="""
            <div style='background: linear-gradient(135deg, #2E86AB 0%, #1a5278 100%); 
                        color: white; padding: 20px; border-radius: 5px; margin-bottom: 10px;'>
                <h1 style='margin: 0; font-size: 28px;'>🎨 Mini Plot Application</h1>
                <p style='margin: 5px 0 0 0; font-size: 14px;'>Using bokeh_garden AnnotationWheelZoomTool</p>
                <p style='margin: 5px 0 0 0; font-size: 12px; opacity: 0.9;'>
                    Try scrolling over the plot - the custom tool allows zooming on annotations!
                </p>
            </div>
            """,
			width=800,
			height=120
		)

		self.status_div = Div(
			text=f"""
            <div style='padding: 15px; background: #e8f4f8; border: 2px solid #2E86AB; 
                        border-radius: 5px; font-family: monospace;'>
                <b style='color: #2E86AB;'>📊 Status:</b> Ready | 
                <b style='color: #2E86AB;'>Points:</b> {len(self.data_source)} | 
                <b style='color: #2E86AB;'>Tool:</b> AnnotationWheelZoomTool loaded | 
                <b style='color: #2E86AB;'>Range:</b> [0.00, 12.57]
            </div>
            """,
			width=800,
			height=60
		)

		self.reset_button = Button(
			label="🔄 Reset",
			button_type="success",
			width=150,
			height=40
		)
		self.reset_button.on_click(self.handle_reset)

		self.random_button = Button(
			label="🎲 Random",
			button_type="primary",
			width=150,
			height=40
		)
		self.random_button.on_click(self.handle_random)

		self.sine_button = Button(
			label="〰️ More Sine Waves",
			button_type="warning",
			width=150,
			height=40
		)
		self.sine_button.on_click(self.handle_sine)

		print("[WIDGETS] All widgets created")

	def handle_reset(self):
		"""Reset to default data"""
		print("[RESET] Button clicked")
		self.data_source = self.generate_default_data()
		self.update_plot()
		self.status_div.text = f"<div style='padding: 15px; background: #d4edda;'><b>Status:</b> Reset to default ({len(self.data_source)} points)</div>"

	def handle_random(self):
		"""Generate random data"""
		print("[RANDOM] Button clicked")
		n = np.random.randint(50, 200)
		x = np.sort(np.random.uniform(0, 10, n))
		y = np.random.normal(0, 1, n) + np.sin(x)
		self.data_source = pd.DataFrame({'x': x, 'y': y})
		self.update_plot()
		self.status_div.text = f"<div style='padding: 15px; background: #d4edda;'><b>Status:</b> Random data generated ({n} points)</div>"

	def handle_sine(self):
		"""Generate multiple sine waves"""
		print("[SINE] Button clicked")
		x = np.linspace(0, 10, 200)
		y = np.sin(x) + 0.5 * np.sin(3 * x) + 0.3 * np.sin(5 * x)
		self.data_source = pd.DataFrame({'x': x, 'y': y})
		self.update_plot()
		self.status_div.text = f"<div style='padding: 15px; background: #d4edda;'><b>Status:</b> Multiple sine waves ({len(self.data_source)} points)</div>"

	def update_plot(self):
		"""Update plot with current data"""
		self.line_renderer.data_source.data = {
			'x': self.data_source['x'],
			'y': self.data_source['y']
		}
		self.circle_renderer.data_source.data = {
			'x': self.data_source['x'],
			'y': self.data_source['y']
		}
		print(f"[PLOT] Updated with {len(self.data_source)} points")

	def setup_layout(self):
		"""Create application layout"""
		print("[LAYOUT] Creating layout structure")

		# Controls row
		controls = row(
			self.reset_button,
			self.random_button,
			self.sine_button,
			height=60
		)

		# Info box
		info_div = Div(
			text="""
            <div style='padding: 10px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 5px; margin: 10px 0;'>
                <b>💡 Tip:</b> Use your mouse wheel to zoom in/out on the plot. 
                The AnnotationWheelZoomTool allows zooming on both data and annotations!
            </div>
            """,
			width=800,
			height=50
		)

		# Main layout
		layout = column(
			self.title_div,
			self.status_div,
			controls,
			info_div,
			self.figure,
			width=800
		)

		print(f"[LAYOUT] Layout created with {len(layout.children)} children")
		print(f"[LAYOUT] Current doc.roots: {len(self.doc.roots)}")

		# Add to document
		self.doc.add_root(layout)
		self.doc.title = "Mini Plot App - AnnotationWheelZoomTool"

		print(f"[LAYOUT] Layout added! Final doc.roots: {len(self.doc.roots)}")


# Create the document
print("=" * 60)
print("[MODULE] Creating document using curdoc()")
print("=" * 60)

try:
	doc = curdoc()
	print(f"[MODULE] Got curdoc: {doc}")
	print("[MODULE] Creating MiniPlotApp...")
	app = MiniPlotApp(doc)
	print("[MODULE] MiniPlotApp created successfully!")
	print(f"[MODULE] Document now has {len(doc.roots)} root(s)")
except Exception as e:
	print(f"[ERROR] Failed to create app: {e}")
	traceback.print_exc()
	raise

print("[MODULE] mini_app_advanced.py initialization complete")
