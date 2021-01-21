import bokeh.io
import bokeh_garden
import pandas as pd
import tempfile
import pygrib
import bokeh.models.sources
import io
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.setLevel(logging.ERROR)

# logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
# #
file_handler = logging.FileHandler('test2.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.ERROR)

logger.addHandler(file_handler)


def get_grib_layer_info(grib):
    print("get grib layer info")
    layerdatas = []
    for layeridx in range(1, grib.messages + 1):
        layer = grib.message(layeridx)
        logger.info('Get grib layer info')
        def getval(g, name):
            try:
                return g[name]
            except:
                return None
        layerdatas.append({key:value for key, value in ((key, getval(layer, key)) for key in layer.keys())
                           if not hasattr(value, "__len__") or len(value) < 20})
    return pd.DataFrame(layerdatas)
    logger.info('DataFrame')

class DownloadContent(object):
    # logger = logging.getLogger(__name__)
    # logger.setLevel(logging.INFO)
    # formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

    def __init__(self, app):
        self.app = app
        logger.info('Download Content')
        try:
            print(y)
        except NameError:
            logger.exception('Another exception occurred')

    def __bytes__(self):
        print("bytes")
        layer_info = get_grib_layer_info(self.app.grib.grib)
        logger.info('Bytes')
        print("layer info", layer_info)
        with io.StringIO() as f:
            layer_info.to_csv(f)
            F = f.getvalue().encode("utf-8")

            print(F)
            return F



class GribInfoDownload(bokeh_garden.application.AppWidget, bokeh.models.layouts.Column):
    # logger = logging.getLogger(__name__)
    # logger.setLevel(logging.INFO)
    # formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

    def __init__(self, app, **kw):
        self._app = app
        logger.info('GRIB info download')
        try:
            print(y)
        except NameError:
            logger.exception('Another exception occurred')

        self._link = bokeh_garden.download.Download(
            text="Download layer information as CSV",
            filename="layers.csv",
            content=DownloadContent(self._app))

        bokeh.models.layouts.Column.__init__(self, self._link, **kw)

