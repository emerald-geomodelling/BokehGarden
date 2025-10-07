import bokeh.models.tools
import bokeh.util.compiler
import bokeh.core.properties

TS_CODE = """
import {ActionTool, ActionToolView} from "models/tools/actions/action_tool"
import * as p from "core/properties"
import {ButtonClick} from "core/bokeh_events"

export class CustomActionToolView extends ActionToolView {
  declare model: CustomActionTool

  override doit(): void {
    this.model.trigger_event(new ButtonClick())
  }
}

export namespace CustomActionTool {
  export type Attrs = p.AttrsOf<Props>
  export type Props = ActionTool.Props & {
    tool_name: p.Property<string | null>
  }
}

export interface CustomActionTool extends ActionTool.Attrs {}

export class CustomActionTool extends ActionTool {
  declare properties: CustomActionTool.Props
  declare __view_type__: CustomActionToolView

  constructor(attrs?: Partial<CustomActionTool.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = CustomActionToolView
    this.define<CustomActionTool.Props>(({Nullable, String}) => ({
      tool_name: [ Nullable(String), "" ],
    }))
  }
}
"""

class CustomActionTool(bokeh.models.tools.ActionTool):
    __implementation__ = bokeh.util.compiler.TypeScript(TS_CODE, file="custom_action_tool.ts")
    tool_name = bokeh.core.properties.String(
        default="",
        help="""Hover title""")
