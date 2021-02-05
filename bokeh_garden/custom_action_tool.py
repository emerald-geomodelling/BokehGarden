import bokeh.models.tools
import bokeh.util.compiler
import bokeh.core.properties

TS_CODE = """
import {ActionTool, ActionToolView} from "models/tools/actions/action_tool"
import * as p from "core/properties"
import {ButtonClick} from "core/bokeh_events"

export class CustomActionToolView extends ActionToolView {
  model: CustomActionTool

  doit(): void {
    this.model.trigger_event(new ButtonClick())
  }
}

export namespace CustomActionTool {
  export type Attrs = p.AttrsOf<Props>

  export type Props = ActionTool.Props & {
    icon: p.Property<string | null>
    tool_name: p.Property<string | null>
  }
}

export interface CustomActionTool extends CustomActionTool.Attrs {}

export class CustomActionTool extends ActionTool {
  properties: CustomActionTool.Props
  __view_type__: CustomActionToolView

  constructor(attrs?: Partial<CustomActionTool.Attrs>) {
    super(attrs)
  }

  static init_CustomActionTool(): void {
    this.prototype.default_view = CustomActionToolView

    this.register_alias("reset_ratio", () => new CustomActionTool())
    this.define<CustomActionTool.Props>(({String, Nullable}) => ({
      icon:       [ Nullable(String), "" ],
      tool_name:  [ Nullable(String), "" ],
    }))
  }

  tool_name : never
  icon : never
}
"""

class CustomActionTool(bokeh.models.tools.Action):
    __implementation__ = bokeh.util.compiler.TypeScript(TS_CODE)

    icon = bokeh.core.properties.String(
        default="",
        help="""data:image URI of icon to render""")
    tool_name = bokeh.core.properties.String(
        default="",
        help="""Hover title""")
