import bokeh.models
import bokeh.util.compiler

TS_CODE = """
import {WheelZoomToolView, WheelZoomTool} from "models/tools/gestures/wheel_zoom_tool"
import {RendererView} from "models/renderers/renderer"
import {reversed} from "core/util/array"
import {ScrollEvent} from "core/ui_events"

export class AnnotationWheelZoomToolView extends WheelZoomToolView {
  model: AnnotationWheelZoomTool

  annotation: any

  _hit_test_renderers(sx: number, sy: number): RendererView | null {
    const views = this.plot_view.get_renderer_views()

    for (const view of reversed(views)) {
      const {level} = view.model
      if ((level == 'annotation' || level == 'overlay') && view.interactive_hit != null) {
        if (view.interactive_hit(sx, sy))
          return view
      }
    }

    return null
  }

  _scroll(ev: ScrollEvent): void {
    this.annotation = this._hit_test_renderers(ev.sx, ev.sy)

    if (this.annotation && !this.annotation._scroll) this.annotation = null;

    if (this.annotation) {
      this.annotation._scroll(ev)
    } else {
      WheelZoomToolView.prototype._scroll.call(this, ev)
    }
  }
}

export class AnnotationWheelZoomTool extends WheelZoomTool {
  __view_type__: AnnotationWheelZoomToolView

  constructor(attrs?: Partial<WheelZoomTool.Attrs>) {
    super(attrs)
  }

  static init_AnnotationWheelZoomTool(): void {
    this.prototype.default_view = AnnotationWheelZoomToolView
    this.register_alias("annotation_wheel_zoom_tool", () => new AnnotationWheelZoomTool({}))
  }
}
"""

class AnnotationWheelZoomTool(bokeh.models.WheelZoomTool):
    __implementation__ = bokeh.util.compiler.TypeScript(TS_CODE)

bokeh.models.Tool.register_alias("annotation_wheel_zoom_tool", lambda: AnnotationWheelZoomTool())
