# annotation_pan_tool.py
import bokeh.models
import bokeh.util.compiler

TS_CODE = """
import {PanToolView, PanTool} from "models/tools/gestures/pan_tool"
import {RendererView} from "models/renderers/renderer"
import {reversed} from "core/util/array"
import {PanEvent} from "core/ui_events"

export class AnnotationPanToolView extends PanToolView {
  declare model: AnnotationPanTool
  annotation: any

  _hit_test_renderers(sx: number, sy: number): RendererView | null {
    const views = [...this.plot_view.renderer_views.values()]
    for (const view of reversed(views)) {
      const {level} = view.model
      if ((level == 'annotation' || level == 'overlay') && view.interactive_hit != null) {
        if (view.interactive_hit(sx, sy))
          return view
      }
    }
    return null
  }

  override _pan_start(ev: PanEvent): void {
    this.annotation = this._hit_test_renderers(ev.sx, ev.sy)
    if (this.annotation && !this.annotation._pan_start) this.annotation = null;
    if (this.annotation) {
      this.annotation._pan_start(ev, this.model.dimensions)
    } else {
      super._pan_start(ev)
    }
  }

  override _pan(ev: PanEvent): void {
    if (this.annotation) {
      this.annotation._pan(ev, this.model.dimensions)
    } else {
      super._pan(ev)
    }
  }

  override _pan_end(ev: PanEvent): void {
    if (this.annotation) {
      this.annotation._pan_end(ev, this.model.dimensions)
    } else {
      super._pan_end(ev)
    }
  }
}

export class AnnotationPanTool extends PanTool {
  declare __view_type__: AnnotationPanToolView

  static {
    this.prototype.default_view = AnnotationPanToolView
  }
}
"""

class AnnotationPanTool(bokeh.models.PanTool):
    __implementation__ = bokeh.util.compiler.TypeScript(TS_CODE, file="annotation_pan_tool.ts")

bokeh.models.Tool.register_alias("annotation_pan_tool", lambda: AnnotationPanTool(dimensions="both"))
