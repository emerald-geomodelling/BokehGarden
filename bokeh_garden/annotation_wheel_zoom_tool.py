# annotation_wheel_zoom_tool.py
import bokeh.models
import bokeh.util.compiler

TS_CODE = """
import {WheelZoomToolView, WheelZoomTool} from "models/tools/gestures/wheel_zoom_tool"
import {RendererView} from "models/renderers/renderer"
import {reversed} from "core/util/array"
import {ScrollEvent} from "core/ui_events"

export class AnnotationWheelZoomToolView extends WheelZoomToolView {
  declare model: AnnotationWheelZoomTool
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

  override _scroll(ev: ScrollEvent): boolean {
    this.annotation = this._hit_test_renderers(ev.sx, ev.sy)
    if (this.annotation && !this.annotation._scroll) this.annotation = null;
    if (this.annotation) {
      this.annotation._scroll(ev)
      return true
    } else {
      return super._scroll(ev)
    }
  }
}

export class AnnotationWheelZoomTool extends WheelZoomTool {
  declare __view_type__: AnnotationWheelZoomToolView

  static {
    this.prototype.default_view = AnnotationWheelZoomToolView
  }
}
"""

class AnnotationWheelZoomTool(bokeh.models.WheelZoomTool):
    __implementation__ = bokeh.util.compiler.TypeScript(TS_CODE, file="annotation_wheel_zoom_tool.ts")

bokeh.models.Tool.register_alias("annotation_wheel_zoom_tool", lambda: AnnotationWheelZoomTool())
