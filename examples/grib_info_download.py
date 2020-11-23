import bokeh.io
import bokeh_garden
import pandas as pd
import tempfile
import pygrib
import bokeh.models.sources
import io

def get_grib_layer_info(grib):
    layerdatas = []
    for layeridx in range(1, grib.messages + 1):
        layer = grib.message(layeridx)
        def getval(g, name):
            try:
                return g[name]
            except:
                return None
        layerdatas.append({key:value for key, value in ((key, getval(layer, key)) for key in layer.keys())
                           if not hasattr(value, "__len__") or len(value) < 20})
    return pd.DataFrame(layerdatas)

class DownloadContent(object):
    def __init__(self, app):
        self.app = app
        
    def __bytes__(self):
        layer_info = get_grib_layer_info(self.app.grib.grib)
        with io.StringIO() as f:
            layer_info.to_csv(f)
            return f.getvalue().encode("utf-8")   

class GribInfoDownload(bokeh_garden.application.AppWidget, bokeh.models.layouts.Column):
    def __init__(self, app, **kw):
        self._app = app

        self._link = bokeh_garden.download.Download(
            text="Download layer information as CSV",
            filename="layers.csv",
            content=DownloadContent(self._app))

        bokeh.models.layouts.Column.__init__(self, self._link, **kw)
