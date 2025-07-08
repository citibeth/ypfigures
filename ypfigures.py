from bokeh.sampledata.gapminder import population, fertility, life_expectancy
from bokeh.models import Button, Slider
from bokeh.plotting import figure, column, row
from bokeh.io import curdoc
import pandas as pd

import time
import numpy as np

from bokeh.io import curdoc, show
from bokeh.models import ColumnDataSource, Grid, Line, LinearAxis, Plot

"""Welcome to YP Figures, where we get to direct a Yellow Pig making
figures on the ice!  To play this game, you will need a Conda Python
environment with the packages:
    numpy, pandas, bokeh

If you are new to Conda:
  1. Install Miniconda:
     https://www.anaconda.com/docs/getting-started/miniconda/main
  2. Configure to use conda-forge
  3. Create an environment (call it yp of course)
  4. Activate the new environment
  5. Run:  conda install numpy pandas bokeh


Once you have your Python set up, run from the command line:

   $ bokeh serve --show ypfigures.py

Copyright (c) 2025 by Elizabeth Fischer
GPL v3 License
"""

class YPTracker:
    def recenter(self):
        # History of trajectory
        self.xx = list()
        self.yy = list()

        # YP Skater State Variables
        self.t = 0
        self.x = 0    # Position
        self.y = 0
        self.v = 1    # Linear speed
        self.theta = 0    # Direction of travel, 0=due East

    def __init__(self):
        """
        """
        self.recenter()

    def update(self, dtheta_dt, delta_t):
        """
        Simple explicit integration
        delta_t:
            Size of timestep
        """
        if np.abs(dtheta_dt) < .000001:
            # Account for straight line, r=inf
            theta1 = self.theta
            len = self.v * delta_t
            x1 = self.x + len * np.cos(self.theta)
            y1 = self.y + len * np.sin(self.theta)
        else:
            r = self.v / dtheta_dt    # TODO: 
            theta0 = self.theta
            theta1 = theta0 + dtheta_dt * delta_t
            phi0 = theta0 - 0.5*np.pi
            phi1 = theta1 - 0.5*np.pi
            x1 = self.x + r * (np.cos(phi1) - np.cos(phi0))
            y1 = self.y + r * (np.sin(phi1) - np.sin(phi0))

        # Add to history
        self.xx.append(x1)
        self.yy.append(y1)

        # Update state
        self.t += delta_t
        self.theta = theta1
        self.x = x1
        self.y = y1

class YPWidgets:
    def __init__(self, fig, yp, delta_t):
        self.fig = fig
        self.yp = yp
        self.delta_t = delta_t

        self.slider = Slider(start=-0.5, end=0.5, value=-0.10, step=.003, title="Steering", format='0.2f')
        self.clear_button = Button(label="Clear")
        self.recenter_button = Button(label="Recenter")
        self.play_button = Button(label="Play")
        self.lines = [fig.line(x='x', y='y', line_width=2, source=ColumnDataSource(dict(x=yp.xx, y=yp.yy)))]

        self.callback = None

        self.play_button.on_click(self.execute_animation)
        self.recenter_button.on_click(self.on_recenter)
        self.clear_button.on_click(self.on_clear)

        ## GUI
        curdoc().add_root(column(
            row(self.clear_button, self.recenter_button, self.play_button),
            self.slider,
            self.fig))

    def update(self):
        self.yp.update(-np.tan(self.slider.value), self.delta_t)
#        yp.update(-slider.value, delta_t)
        self.lines[-1].data_source.data = {'x': self.yp.xx, 'y': self.yp.yy}

    def execute_animation(self):
        if self.callback is None:
            self.play_button.label = "Pause"
            self.callback = curdoc().add_periodic_callback(self.update, 20)
        else:
            self.play_button.label = "Play"
            curdoc().remove_periodic_callback(self.callback)
            self.callback = None

    def on_recenter(self):
        if self.callback is not None:
            self.play_button.label = "Play"
            curdoc().remove_periodic_callback(self.callback)
            self.callback = None
        self.yp.recenter()
        self.lines.append(self.fig.line(x='x', y='y', line_width=2, source=ColumnDataSource(dict(x=self.yp.xx, y=self.yp.yy))))


    def on_clear(self):
        self.on_recenter()
        for line in self.lines:
            line.data_source.data = {'x': [], 'y': []}


def main():
    fig = figure(x_range=(-30,30), y_range=(-30,30), width=900, height=900,
                 title = "Yellow Pig Loops")

    yp = YPTracker()
    delta_t = .1
    YPWidgets(fig, yp, delta_t)
        
main()
