import bokeh.io
import bokeh_garden
import pandas as pd
import tempfile
import pygrib
import bokeh.models.sources
import logging
import examples.bokeh_handler
#from bokeh.io import show
#from bokeh.models import Div

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.setLevel(logging.ERROR)
# logger.setLevel(logging.DEBUG)

# formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
#
# file_handler = logging.FileHandler('test2.log')
# file_handler.setFormatter(formatter)
# file_handler.setLevel(logging.ERROR)
# file_handler.setFormatter(formatter)
# #
# logger.addHandler(file_handler)
#
# logger.setLevel(logging.INFO)


class GribContainer(bokeh_garden.application.AppWidget, bokeh.models.sources.DataSource):
    def __init__(self, grib):
        self._grib = grib

        logger.info('Grib Container')



    @property
    def grib(self): return self._grib
    print('GribContainer A')

class GribUpload(bokeh_garden.application.AppWidget, bokeh.models.layouts.Column):

    def __init__(self, app, **kw):
        self._app = app
        self._upload = bokeh_garden.upload.Upload()
        bokeh.models.layouts.Column.__init__(self, self._upload, **kw)
        print("Before File uploaded")
        self._upload.on_change("value", self.file_uploaded)
        print("After File uploaded")
        logger.info('Grib Upload')


    def file_uploaded(self, attr, old, new):
        print("File uploaded function")
        with tempfile.NamedTemporaryFile() as f:
            f.write(self._upload.value_bytes)
            print("App.grib before")
            self._app.grib = GribContainer(pygrib.open(f.name))
            print("App.grib after", f.name)
        logger.info('Grib File Uploaded')

        try:
            print(x)
        except NameError:
            logger.exception('An exception occurred')



            
