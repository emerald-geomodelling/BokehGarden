import numpy as np

from bokeh.models import ColorBar
from bokeh.plotting import figure, show
from bokeh.util.compiler import TypeScript
from bokeh.io import show, output_notebook

TS_CODE = """
import * as p from "core/properties"
import {ColorBar, ColorBarView} from "models/annotations/color_bar"
import {PanEvent} from "core/ui_events"
import {ScrollEvent} from "core/ui_events"

declare const window: any

export class InteractiveColorBarView extends ColorBarView {
  model: InteractiveColorBar

  low: any
  high: any
  ev: PanEvent

  interactive_hit(sx: number, sy: number): boolean {
    let size = this.compute_legend_dimensions()
    let loc = this.compute_legend_location()
  
    return sx >= loc.sx && sx <= loc.sx + size.width && sy >= loc.sy && sy <= loc.sy + size.height
  }
  on_hit(_sx: number, _sy: number): boolean {
    return true;
  }
  cursor(_sx: number, _sy: number): string | null {
    return null;
  }
  _pan_start(ev: PanEvent, _dimension: string) {
    this.low = this.model.color_mapper.low
    this.high = this.model.color_mapper.high
    this.ev = ev
  }
  _pan(ev: PanEvent, _dimension: string) {
    let size = this.compute_legend_dimensions()
    var dist = (ev.sy - this.ev.sy) / size.height

    if (this.model.color_mapper.type == "LogColorMapper") {
      var high = Math.log10(this.high);
      var low = Math.log10(this.low)
      var change = (high - low) * dist
      low = low + dist
      high = high + dist
      this.model.color_mapper.low = Math.pow(10, low)
      this.model.color_mapper.high = Math.pow(10, high)
    } else {
      var change = (this.high - this.low) * dist
      this.model.color_mapper.low = this.low + change
      this.model.color_mapper.high = this.high + change
   }

    this._fixRange()
  }
  _pan_end(_ev: PanEvent, _dimension: string) {
  }
  _scroll(ev: ScrollEvent) {
    // This zooms around the mouse position

    if (this.model.color_mapper.low === null || this.model.color_mapper.high === null) return

    let size = this.compute_legend_dimensions()
    let loc = this.compute_legend_location()

    var pos = (ev.sy - loc.sy) / size.height

    var high = this.model.color_mapper.high
    var low = this.model.color_mapper.low

    if (this.model.color_mapper.type == "LogColorMapper") {
      high = Math.log10(high);
      low = Math.log10(low)
    }

    var value = high * (1 - pos) + low * pos
    var low = low - value
    var high = high - value

    var delta = 1 - ev.delta*1/600

    low = low * delta + value
    high = high * delta + value

    if (this.model.color_mapper.type == "LogColorMapper") {
      high = Math.pow(10, high)
      low = Math.pow(10, low)
    }

    this.model.color_mapper.low = low
    this.model.color_mapper.high = high

    this._fixRange()
  }
  _fixRange() {
    if (this.model.color_mapper.low === null || this.model.color_mapper.high === null) return

    if (this.model.color_mapper.type == "LogColorMapper") {
      if (this.model.color_mapper.low <= 0) this.model.color_mapper.low = 1e-100
    }
    if (this.model.color_mapper.high <= this.model.color_mapper.low) {
      this.model.color_mapper.high = this.model.color_mapper.low + 1e-100
    }
  }
}

export namespace InteractiveColorBar {
  export type Attrs = p.AttrsOf<Props>

  export type Props = ColorBar.Props
}

export interface InteractiveColorBar extends InteractiveColorBar.Attrs {}

export class InteractiveColorBar extends ColorBar {
  properties: InteractiveColorBar.Props
  __view_type__: InteractiveColorBarView

  constructor(attrs?: Partial<InteractiveColorBar.Attrs>) {
    super(attrs)
  }

  static init_InteractiveColorBar() {
    this.prototype.default_view = InteractiveColorBarView
  }
  
}
"""

class InteractiveColorBar(ColorBar):
    __implementation__ = TypeScript(TS_CODE)
