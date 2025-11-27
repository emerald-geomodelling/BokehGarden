# interactive_color_bar.py - FINAL WORKING VERSION for Bokeh 3.x

import numpy as np
from bokeh.models import ColorBar
from bokeh.util.compiler import TypeScript

TS_CODE = """
import * as p from "core/properties"
import {ColorBar, ColorBarView} from "models/annotations/color_bar"

export class InteractiveColorBarView extends ColorBarView {
  declare model: InteractiveColorBar
  low: any
  high: any
  drag_start_y: number | null = null
  _wheel_handler: ((e: WheelEvent) => void) | null = null
  _mouse_down_handler: ((e: MouseEvent) => void) | null = null
  _mouse_move_handler: ((e: MouseEvent) => void) | null = null
  _mouse_up_handler: ((e: MouseEvent) => void) | null = null

  // Check if coordinates are over the color bar
  _is_over_bar(sx: number, sy: number): boolean {
    const size: any = (this as any).compute_legend_dimensions()
    const loc: any = (this as any).compute_legend_location()
    return sx >= loc.sx && sx <= loc.sx + size.width &&
           sy >= loc.sy && sy <= loc.sy + size.height
  }

  override after_layout(): void {
    super.after_layout?.()
    this._setup_event_listeners()
  }

  _setup_event_listeners(): void {
    const canvas_el = this.plot_view.canvas_view.events_el

    // Remove old listeners if they exist
    if (this._wheel_handler) {
      canvas_el.removeEventListener("wheel", this._wheel_handler)
    }
    if (this._mouse_down_handler) {
      canvas_el.removeEventListener("mousedown", this._mouse_down_handler)
    }
    if (this._mouse_move_handler) {
      canvas_el.removeEventListener("mousemove", this._mouse_move_handler)
    }
    if (this._mouse_up_handler) {
      canvas_el.removeEventListener("mouseup", this._mouse_up_handler)
    }

    // Create new handlers
    this._wheel_handler = (e: WheelEvent) => {
      const sx = e.offsetX
      const sy = e.offsetY

      if (this._is_over_bar(sx, sy)) {
        e.preventDefault()
        e.stopPropagation()
        this._handle_wheel(sx, sy, e.deltaY)
      }
    }

    this._mouse_down_handler = (e: MouseEvent) => {
      const sx = e.offsetX
      const sy = e.offsetY

      if (this._is_over_bar(sx, sy)) {
        e.preventDefault()
        e.stopPropagation()
        this._handle_pan_start(sy)
      }
    }

    this._mouse_move_handler = (e: MouseEvent) => {
      if (this.drag_start_y !== null) {
        e.preventDefault()
        e.stopPropagation()
        this._handle_pan(e.offsetY)
      }
    }

    this._mouse_up_handler = (e: MouseEvent) => {
      if (this.drag_start_y !== null) {
        e.preventDefault()
        e.stopPropagation()
        this._handle_pan_end()
      }
    }

    // Register new listeners
    canvas_el.addEventListener("wheel", this._wheel_handler, {passive: false})
    canvas_el.addEventListener("mousedown", this._mouse_down_handler)
    canvas_el.addEventListener("mousemove", this._mouse_move_handler)
    canvas_el.addEventListener("mouseup", this._mouse_up_handler)
  }

  override remove(): void {
    // Clean up event listeners
    const canvas_el = this.plot_view.canvas_view.events_el
    if (this._wheel_handler) {
      canvas_el.removeEventListener("wheel", this._wheel_handler)
    }
    if (this._mouse_down_handler) {
      canvas_el.removeEventListener("mousedown", this._mouse_down_handler)
    }
    if (this._mouse_move_handler) {
      canvas_el.removeEventListener("mousemove", this._mouse_move_handler)
    }
    if (this._mouse_up_handler) {
      canvas_el.removeEventListener("mouseup", this._mouse_up_handler)
    }
    super.remove()
  }

  _handle_pan_start(sy: number): void {
    const mapper: any = this.model.color_mapper
    this.low = mapper.low
    this.high = mapper.high
    this.drag_start_y = sy
  }

  _handle_pan(sy: number): void {
    if (this.drag_start_y === null) return

    const size: any = (this as any).compute_legend_dimensions()
    const mapper: any = this.model.color_mapper
    const dist = (sy - this.drag_start_y) / size.height

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

  _handle_pan_end(): void {
    this.drag_start_y = null
  }

  _handle_wheel(_sx: number, sy: number, delta: number): void {
    const mapper: any = this.model.color_mapper
    if (mapper.low === null || mapper.high === null) return

    const size: any = (this as any).compute_legend_dimensions()
    const loc: any = (this as any).compute_legend_location()
    const pos = (sy - loc.sy) / size.height
    let high = mapper.high
    let low = mapper.low

    if (mapper.type == "LogColorMapper") {
      high = Math.log10(high)
      low = Math.log10(low)
    }

    const value = high * (1 - pos) + low * pos
    low = low - value
    high = high - value
    const zoom_delta = 1 - delta * 1/600
    low = low * zoom_delta + value
    high = high * zoom_delta + value

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
