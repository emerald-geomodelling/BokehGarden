import bokeh.models
import bokeh.util.compiler

TS_CODE = """
import {PanToolView, PanTool} from "models/tools/gestures/pan_tool"
import {RendererView} from "models/renderers/renderer"
import {reversed} from "core/util/array"
import {PanEvent} from "core/ui_events"

export class AnnotationPanToolView extends PanToolView {
  model: AnnotationPanTool

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

  _pan_start(ev: PanEvent): void {
    this.annotation = this._hit_test_renderers(ev.sx, ev.sy)

    if (this.annotation && !this.annotation._pan_start) this.annotation = null;

    if (this.annotation) {
      this.annotation._pan_start(ev, this.model.dimensions)
    } else {
      PanToolView.prototype._pan_start.call(this, ev)
    }
  }

  _pan(ev: PanEvent): void {
    if (this.annotation) {
      this.annotation._pan(ev, this.model.dimensions)
    } else {
      PanToolView.prototype._pan.call(this, ev)
    }
  }

  _pan_end(ev: PanEvent): void {
    if (this.annotation) {
      this.annotation._pan_end(ev, this.model.dimensions)
    } else {
      PanToolView.prototype._pan_end.call(this, ev)
    }
  }
}

export class AnnotationPanTool extends PanTool {
  __view_type__: AnnotationPanToolView

  constructor(attrs?: Partial<PanTool.Attrs>) {
    super(attrs)
  }

  static init_AnnotationPanTool(): void {
    this.prototype.default_view = AnnotationPanToolView
    this.register_alias("annotation_pan_tool", () => new AnnotationPanTool({dimensions: 'both'}))
  }
}
"""

class AnnotationPanTool(bokeh.models.PanTool):
    __implementation__ = bokeh.util.compiler.TypeScript(TS_CODE)

bokeh.models.Tool.register_alias("annotation_pan_tool", lambda: AnnotationPanTool(dimensions="both"))
