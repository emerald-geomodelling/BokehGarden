import tornado.escape
import tornado.ioloop
import tornado.auth
import bokeh.application
import bokeh.application.handlers
import bokeh.server.server
import os
import sys
import urllib.parse
import bokeh.server.auth_provider

import examples.weather_data_explorer

def main():    
    io_loop = tornado.ioloop.IOLoop.current()
    bokeh_app = bokeh.application.Application(bokeh.application.handlers.FunctionHandler(
        examples.weather_data_explorer.WeatherDataExplorer()))

    server = bokeh.server.server.Server(
        {"/app": bokeh_app},
        io_loop=io_loop)
    
    server.start()

    io_loop.add_callback(server.show, "/")
    io_loop.start()

if __name__ == "__main__":
    main()

