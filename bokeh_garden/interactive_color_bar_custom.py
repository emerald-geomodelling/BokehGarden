# interactive_color_bar_custom.py - Custom Interactive ColorBar with UI Controls
"""
Alternative approach to interactive color bar using explicit UI controls:
- Buttons for zoom in/out
- Buttons for shift up/down (pan)
- Text inputs for precise min/max values
- Reset button
"""

from bokeh.models import ColorBar, Button, TextInput, Spacer, LogTicker, LogColorMapper
from bokeh.layouts import column, row
from bokeh.models.widgets import Div
from bokeh.plotting import figure


class InteractiveColorBarCustom:
    """
    Custom interactive color bar with explicit UI controls.

    This provides an alternative to mouse-based interaction by offering:
    - Zoom In/Out buttons (10% zoom steps)
    - Shift Up/Down buttons (10% shift steps)
    - Text inputs for precise min/max control
    - Reset button to restore original range
    - Auto-update toggle

    Usage:
        mapper = LinearColorMapper(palette=Viridis256, low=0, high=100)
        color_bar_widget = InteractiveColorBarCustom(color_mapper=mapper)
        layout = column(plot, color_bar_widget.layout)
    """

    def __init__(self, color_mapper, title="Color Range", width=200, show_text_inputs=True, target_figure=None, zoom_percent=5):
        """
        Initialize the interactive color bar with controls.

        Args:
            color_mapper: The ColorMapper instance to control
            title: Title for the control panel
            width: Width of the control panel (ColorBar will be 1/3 of this)
            show_text_inputs: Whether to show text input fields for precise control
            target_figure: The figure to add the ColorBar to. If None, creates a standalone figure.
            zoom_percent: Percentage to zoom in/out by (default 5%)
        """
        self.color_mapper = color_mapper
        self.original_low = color_mapper.low
        self.original_high = color_mapper.high
        self.original_palette = color_mapper.palette.copy() if hasattr(color_mapper.palette, 'copy') else list(color_mapper.palette)
        self.width = width
        self.show_text_inputs = show_text_inputs
        self.target_figure = target_figure
        self.zoom_percent = zoom_percent / 100.0  # Convert to decimal

        # If a target figure is provided, add ColorBar to it directly
        # Otherwise create a minimal standalone figure
        if target_figure is not None:
            self.color_bar_figure = target_figure
        else:
            # Create a minimal figure to hold the color bar
            # ColorBar must be added to a figure, it can't exist standalone
            self.color_bar_figure = figure(
                width=width,
                height=300,
                toolbar_location=None,
                min_border=0,
                outline_line_color=None
            )
            # Remove axes and grid
            self.color_bar_figure.axis.visible = False
            self.color_bar_figure.grid.visible = False
            self.color_bar_figure.xaxis.visible = False
            self.color_bar_figure.yaxis.visible = False

        # Create and add the color bar to the figure
        # If using a LogColorMapper, add a LogTicker for proper logarithmic display
        # ColorBar width is 1/3 of the control panel width
        colorbar_kwargs = {
            'color_mapper': color_mapper,
            'width': int(width / 3),
            'title': title
        }

        # Position differently based on whether it's a standalone figure or added to existing
        if target_figure is None:
            colorbar_kwargs['location'] = (0, 0)
        else:
            # Add to the right side of the existing figure
            colorbar_kwargs['location'] = 'right'

        if isinstance(color_mapper, LogColorMapper):
            colorbar_kwargs['ticker'] = LogTicker()

        self.color_bar = ColorBar(**colorbar_kwargs)

        # Add the ColorBar to the figure
        if target_figure is None:
            self.color_bar_figure.add_layout(self.color_bar, 'center')
        else:
            # Add to right side of existing figure
            self.color_bar_figure.add_layout(self.color_bar, 'right')

        # Create control widgets
        self._create_controls()

        # Add listeners to color mapper to trigger color bar updates
        self.color_mapper.on_change('low', self._on_mapper_change)
        self.color_mapper.on_change('high', self._on_mapper_change)

        # Build the layout
        self.layout = self._build_layout()

    def _on_mapper_change(self, attr, old, new):
        """Callback when color mapper low/high changes."""
        # Force redraw by toggling a property
        # This is a workaround to make the ColorBar update its display
        pass

    def _create_controls(self):
        """Create all control widgets."""
        # Title
        self.title_div = Div(
            text=f"<b>Color Range Controls</b>",
            width=self.width,
            height=25
        )

        # Debug info showing actual color mapper values
        self.debug_div = Div(
            text=f"Range: {self.color_mapper.low:.2f} - {self.color_mapper.high:.2f}",
            width=self.width,
            height=20
        )

        # Zoom controls - stacked vertically, same width
        button_width = self.width
        self.zoom_in_btn = Button(
            label="Zoom In",
            button_type="success",
            width=button_width
        )
        self.zoom_in_btn.on_click(self._zoom_in)

        self.zoom_out_btn = Button(
            label="Zoom Out",
            button_type="success",
            width=button_width
        )
        self.zoom_out_btn.on_click(self._zoom_out)

        # Reset button - same width as zoom buttons
        self.reset_btn = Button(
            label="Reset Range",
            button_type="warning",
            width=button_width
        )
        self.reset_btn.on_click(self._reset_range)

        # Text inputs for precise control (optional) - stacked vertically
        if self.show_text_inputs:
            self.min_input = TextInput(
                title="Min:",
                value=f"{self.color_mapper.low:.4g}",
                width=self.width
            )
            self.min_input.on_change('value', self._on_min_change)

            self.max_input = TextInput(
                title="Max:",
                value=f"{self.color_mapper.high:.4g}",
                width=self.width
            )
            self.max_input.on_change('value', self._on_max_change)

    def _build_layout(self):
        """Build the complete layout with color bar and controls - all stacked vertically."""
        components = [
            self.title_div,
            self.debug_div,
        ]

        # Only include the color bar figure if it's a standalone figure
        # (not added to an existing target figure)
        if self.target_figure is None:
            components.append(self.color_bar_figure)

        # Add zoom buttons (stacked vertically)
        components.extend([
            self.zoom_in_btn,
            self.zoom_out_btn,
            self.reset_btn
        ])

        # Add text inputs (stacked vertically)
        if self.show_text_inputs:
            components.extend([
                self.min_input,
                self.max_input
            ])

        return column(*components, width=self.width)

    def _trigger_change(self):
        """Trigger a change to update the color bar display."""
        # The ColorBar automatically updates when low/high change
        # We don't need to modify the palette - just ensure the color mapper
        # uses the full original palette so it matches the plot
        pass

    def _zoom_in(self):
        """Zoom in on the color range."""
        current_range = self.color_mapper.high - self.color_mapper.low
        center = (self.color_mapper.high + self.color_mapper.low) / 2
        new_range = current_range * (1 - self.zoom_percent)

        self.color_mapper.low = center - new_range / 2
        self.color_mapper.high = center + new_range / 2
        self._trigger_change()
        self._update_text_inputs()

    def _zoom_out(self):
        """Zoom out on the color range."""
        current_range = self.color_mapper.high - self.color_mapper.low
        center = (self.color_mapper.high + self.color_mapper.low) / 2
        new_range = current_range * (1 + self.zoom_percent)

        self.color_mapper.low = center - new_range / 2
        self.color_mapper.high = center + new_range / 2
        self._trigger_change()
        self._update_text_inputs()

    def _reset_range(self):
        """Reset to the original color range."""
        self.color_mapper.low = self.original_low
        self.color_mapper.high = self.original_high
        self._update_text_inputs()

    def _update_text_inputs(self):
        """Update text input values to match current mapper range."""
        if self.show_text_inputs:
            self.min_input.value = f"{self.color_mapper.low:.4g}"
            self.max_input.value = f"{self.color_mapper.high:.4g}"
        # Update debug div
        self.debug_div.text = f"Range: {self.color_mapper.low:.2f} - {self.color_mapper.high:.2f}"

    def _on_min_change(self, attr, old, new):
        """Handle min text input change."""
        try:
            new_val = float(new)
            if new_val < self.color_mapper.high:
                self.color_mapper.low = new_val
                self._trigger_change()
        except ValueError:
            # Revert to current value if invalid
            self.min_input.value = f"{self.color_mapper.low:.4g}"

    def _on_max_change(self, attr, old, new):
        """Handle max text input change."""
        try:
            new_val = float(new)
            if new_val > self.color_mapper.low:
                self.color_mapper.high = new_val
                self._trigger_change()
        except ValueError:
            # Revert to current value if invalid
            self.max_input.value = f"{self.color_mapper.high:.4g}"
