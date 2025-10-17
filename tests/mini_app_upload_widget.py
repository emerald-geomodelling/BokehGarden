# BokehGarden/tests/mini_app_upload_widget.py
"""
Mini Plot Application - Using bokeh_garden Upload widget
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

print("[IMPORT] About to import Upload from bokeh_garden")
from bokeh_garden.upload import Upload

print("[IMPORT] Upload imported successfully")


class MiniPlotApp:
	"""Mini application using bokeh_garden Upload widget."""

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
		"""Create the main plot figure"""
		self.figure = figure(
			width=800,
			height=400,
			title="Data Visualization - Mini App",
			x_axis_label='X Axis',
			y_axis_label='Y Axis',
			toolbar_location="above",
			tools="pan,wheel_zoom,box_zoom,reset,save",
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
                <p style='margin: 5px 0 0 0; font-size: 14px;'>Using bokeh_garden Upload Widget</p>
            </div>
            """,
			width=800,
			height=90
		)

		try:
			self.upload_widget = Upload(
				accept=".csv,.txt",
				width=250,
				document=self.doc
			)
			self.upload_widget.on_change('value', self.handle_upload)
			print("[WIDGETS] Upload widget created successfully")
		except Exception as e:
			print(f"[ERROR] Failed to create Upload widget: {e}")
			traceback.print_exc()
			raise

		self.status_div = Div(
			text=f"""
            <div style='padding: 15px; background: #e8f4f8; border: 2px solid #2E86AB; 
                        border-radius: 5px; font-family: monospace;'>
                <b style='color: #2E86AB;'>📊 Status:</b> Ready | 
                <b style='color: #2E86AB;'>Points:</b> {len(self.data_source)} | 
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

		print("[WIDGETS] All widgets created")

	def handle_upload(self, attr, old, new):
		"""Handle file upload"""
		print(f"[UPLOAD] Triggered! attr={attr}")
		try:
			file_bytes = self.upload_widget.file_bytes
			file_content = io.StringIO(file_bytes.decode('utf-8'))
			df = pd.read_csv(file_content)

			if 'x' not in df.columns or 'y' not in df.columns:
				self.status_div.text = "<div style='color: red; padding: 15px; background: #ffe6e6;'><b>Error:</b> CSV must have 'x' and 'y' columns</div>"
				return

			self.data_source = df[['x', 'y']]
			self.update_plot()
			filename = self.upload_widget.filename if self.upload_widget.filename else 'file'
			self.status_div.text = f"<div style='padding: 15px; background: #d4edda;'><b>Uploaded:</b> {filename} ({len(df)} points)</div>"
			print(f"[UPLOAD] Success - {len(df)} points")

		except Exception as e:
			print(f"[ERROR] Upload failed: {e}")
			traceback.print_exc()
			self.status_div.text = f"<div style='color: red; padding: 15px;'><b>Error:</b> {str(e)}</div>"

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

		# Upload controls
		upload_label = Div(
			text="<div style='line-height: 40px; font-weight: bold; font-size: 14px;'>📁 Upload CSV:</div>",
			width=120,
			height=40
		)

		upload_row = row(
			upload_label,
			self.upload_widget,
			self.reset_button,
			self.random_button,
			height=60
		)

		# Spacer
		spacer = Div(text="", width=800, height=15)

		# Main layout
		layout = column(
			self.title_div,
			self.status_div,
			upload_row,
			spacer,
			self.figure,
			width=800
		)

		print(f"[LAYOUT] Layout created with {len(layout.children)} children")
		print(f"[LAYOUT] Current doc.roots: {len(self.doc.roots)}")

		# Add to document
		self.doc.add_root(layout)
		self.doc.title = "Mini Plot App"

		print(f"[LAYOUT] Layout added! Final doc.roots: {len(self.doc.roots)}")


# Create the document - THIS IS THE KEY DIFFERENCE
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

print("[MODULE] mini_app_upload_widget.py initialization complete")
