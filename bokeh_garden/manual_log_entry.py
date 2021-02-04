import bokeh.io
import bokeh.models.sources
import bokeh.models
import logging
import bokeh.models.widgets
import bokeh_garden.application


class ManualLogEntry(bokeh_garden.application.AppWidget, bokeh.models.layouts.Column):

    def __init__(self, app, **kw):
        self._app = app

        self._comments = bokeh.models.TextInput(title="Comments", value="")

        self._comments_button = bokeh.models.widgets.Button(label="Add comments to log", button_type="primary")

        bokeh.models.layouts.Column.__init__(self, self._comments, self._comments_button, **kw)

        self._comments_button.on_click(self.add_comments)

    def add_comments(self):
        logger = logging.getLogger('COMMENT')
        logger.info(self._comments.value)
        self._comments.value =''


