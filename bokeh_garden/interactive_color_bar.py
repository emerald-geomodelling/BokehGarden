# interactive_color_bar.py - FINAL WORKING VERSION for Bokeh 3.x

import numpy as np
from bokeh.models import ColorBar
from bokeh.util.compiler import TypeScript

TS_CODE = """
import * as p from "core/properties"
import {ColorBar, ColorBarView} from "models/annotations/color_bar"
import {PanEvent} from "core/ui_events"
import {ScrollEvent} from "core/ui_events"

export class InteractiveColorBarView extends ColorBarView {
  declare model: InteractiveColorBar
  low: any
  high: any
  ev: PanEvent | null = null

  // DO NOT override interactive_hit() - it blocks all plot tools in Bokeh 3.x
  // DO NOT override on_hit() - not needed
  // DO NOT override cursor() - not needed

  _pan_start(ev: PanEvent): void {
    // Check if we're over the color bar
    const size: any = (this as any).compute_legend_dimensions()
    const loc: any = (this as any).compute_legend_location()
    const over_bar = ev.sx >= loc.sx && ev.sx <= loc.sx + size.width &&
                     ev.sy >= loc.sy && ev.sy <= loc.sy + size.height

    if (!over_bar) {
      this.ev = null
      return  // Not on color bar, let plot tools handle it
    }

    const mapper: any = this.model.color_mapper
    this.low = mapper.low
    this.high = mapper.high
    this.ev = ev
  }

  _pan(ev: PanEvent): void {
    if (this.ev === null) return  // We didn't capture the start, let plot tools handle

    const size: any = (this as any).compute_legend_dimensions()
    const mapper: any = this.model.color_mapper
    const dist = (ev.sy - this.ev.sy) / size.height

    if (mapper.type == "LogColorMapper") {
      let high = Math.log10(this.high)
      let low = Math.log10(this.low)
      const change = (high - low) * dist
      low = low + change
      high = high + change
      mapper.low = Math.pow(10, low)
      mapper.high = Math.pow(10, high)
    } else {
      const change = (this.high - this.low) * dist
      mapper.low = this.low + change
      mapper.high = this.high + change
    }

    this._fixRange()
  }

  _pan_end(_ev: PanEvent): void {
    this.ev = null  // Release capture
  }

  _scroll(ev: ScrollEvent): void {
    // Check if we're over the color bar
    const size: any = (this as any).compute_legend_dimensions()
    const loc: any = (this as any).compute_legend_location()
    const over_bar = ev.sx >= loc.sx && ev.sx <= loc.sx + size.width &&
                     ev.sy >= loc.sy && ev.sy <= loc.sy + size.height

    if (!over_bar) return  // Not on color bar, let plot wheel zoom handle it

    const mapper: any = this.model.color_mapper
    if (mapper.low === null || mapper.high === null) return

    const pos = (ev.sy - loc.sy) / size.height
    let high = mapper.high
    let low = mapper.low

    if (mapper.type == "LogColorMapper") {
      high = Math.log10(high)
      low = Math.log10(low)
    }

    const value = high * (1 - pos) + low * pos
    low = low - value
    high = high - value
    const delta = 1 - ev.delta * 1/600
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
	"""
	Interactive ColorBar for Bokeh 3.x

	- Scroll over color bar to zoom the color range
	- Click and drag on color bar to pan the color range
	- Does NOT block plot tools (pan, zoom work normally on plot)
	"""
	__implementation__ = TypeScript(TS_CODE, file="interactive_color_bar.ts")
