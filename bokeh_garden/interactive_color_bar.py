# interactive_color_bar.py - Fixed variable shadowing
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
  declare model: InteractiveColorBar
  low: any
  high: any
  ev: PanEvent

  override interactive_hit(sx: number, sy: number): boolean {
    const size: any = (this as any).compute_legend_dimensions()
    const loc: any = (this as any).compute_legend_location()
    return sx >= loc.sx && sx <= loc.sx + size.width && sy >= loc.sy && sy <= loc.sy + size.height
  }

  override on_hit(_sx: number, _sy: number): boolean {
    return true;
  }

  override cursor(_sx: number, _sy: number): string | null {
    return null;
  }

  _pan_start(ev: PanEvent, _dimension: string) {
    const mapper: any = this.model.color_mapper
    this.low = mapper.low
    this.high = mapper.high
    this.ev = ev
  }

  _pan(ev: PanEvent, _dimension: string) {
    const size: any = (this as any).compute_legend_dimensions()
    const mapper: any = this.model.color_mapper
    var dist = (ev.sy - this.ev.sy) / size.height
    if (mapper.type == "LogColorMapper") {
      var high = Math.log10(this.high);
      var low = Math.log10(this.low)
      var change = (high - low) * dist
      low = low + dist
      high = high + dist
      mapper.low = Math.pow(10, low)
      mapper.high = Math.pow(10, high)
    } else {
      var change = (this.high - this.low) * dist
      mapper.low = this.low + change
      mapper.high = this.high + change
    }
    this._fixRange()
  }

  _pan_end(_ev: PanEvent, _dimension: string) {
  }

  _scroll(ev: ScrollEvent) {
    const mapper: any = this.model.color_mapper
    if (mapper.low === null || mapper.high === null) return
    const size: any = (this as any).compute_legend_dimensions()
    const loc: any = (this as any).compute_legend_location()
    var pos = (ev.sy - loc.sy) / size.height
    var high = mapper.high
    var low = mapper.low
    if (mapper.type == "LogColorMapper") {
      high = Math.log10(high);
      low = Math.log10(low)
    }
    var value = high * (1 - pos) + low * pos
    low = low - value
    high = high - value
    var delta = 1 - ev.delta*1/600
    low = low * delta + value
    high = high * delta + value
    if (mapper.type == "LogColorMapper") {
      high = Math.pow(10, high)
      low = Math.pow(10, low)
    }
    mapper.low = low
    mapper.high = high
    this._fixRange()
  }

  _fixRange() {
    const mapper: any = this.model.color_mapper
    if (mapper.low === null || mapper.high === null) return
    if (mapper.type == "LogColorMapper") {
      if (mapper.low <= 0) mapper.low = 1e-100
    }
    if (mapper.high <= mapper.low) {
      mapper.high = mapper.low + 1e-100
    }
  }
}

export namespace InteractiveColorBar {
  export type Attrs = p.AttrsOf<Props>
  export type Props = ColorBar.Props
}

export interface InteractiveColorBar extends ColorBar.Attrs {}

export class InteractiveColorBar extends ColorBar {
  declare properties: InteractiveColorBar.Props
  declare __view_type__: InteractiveColorBarView

  constructor(attrs?: Partial<InteractiveColorBar.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = InteractiveColorBarView
  }
}
"""

class InteractiveColorBar(ColorBar):
    __implementation__ = TypeScript(TS_CODE, file="interactive_color_bar.ts")
