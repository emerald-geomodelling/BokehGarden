#!/usr/bin/env python

import setuptools

setuptools.setup(
    name='bokeh-garden',
    version='0.0.7',
    description='Additional widgets for Bokeh',
    long_description="""Additional widgets for Bokeh plots:

* Interactive colorbar that allows adjusting the color map by pan and zoom
* Custom plot tool
* File download / upload widgets without size limit 
* Log viewer that integrates with the python logging framework
* Progress bar
* LaTeX labels
    """,
    long_description_content_type="text/markdown",
    author='Egil Moeller',
    author_email='em@emeraldgeo.no',
    url='https://github.com/EMeraldGeo/BokehGarden',
    packages=setuptools.find_packages(),
    install_requires=[
        "bokeh",
    ]
)
