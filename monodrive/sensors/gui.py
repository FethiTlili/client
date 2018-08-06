
__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

import logging
import monodrive.constants as constants

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

import cv2
import json
import matplotlib
import multiprocessing
import os
import time
import threading
import prctl


matplotlib.use('TkAgg')

RENDER_RUNNING = 2
RENDER_STARTING = 1
RENDER_STOPPED = 0
RENDER_STOPPING = -1

class BaseSensorUI(object):
    Window_Settings_Lock = multiprocessing.Lock()

    def __init__(self, name=None, q_display=None, **kwargs):
        super(BaseSensorUI, self).__init__(**kwargs)
        self.view_lock = threading.Lock()
        self.process_data_thread = None
        self.window_x_position = 0
        self.window_y_position = 0
        self.view_changing_timer = None
        self.previous_event = None
        if name != None:
            self.name = name
        if q_display != None:
            self.q_display = q_display

        manager = multiprocessing.Manager()
        self.render_state = manager.Value('i', RENDER_STOPPED)
        

    def initialize_views(self):
        # override for UI creation
        print("initialize view {0}".format(self.name))
        return

    def render_views(self):
        while self.thread_state.value == RENDER_RUNNING:
            time.sleep(0.1)
        return

    def process_display_data(self):
        # override for main data processing
        #print("process {0}".format(self.name))
        return

    def rendering_main_threaded(self):
        #self.initialize_views()

        # start processing thread
        self.process_data_thread = threading.Thread(target=self.process_data_loop, args=(self,),
                                                    name=self.name + 'Process_Data_Thread')
        self.process_data_thread.start()
        # wait here until thread is running
        #while self.render_state.value != RENDER_RUNNING:
        #    time.sleep(1)

        # mainloop
        self.render_views()

        # cleanup
        self.process_data_thread.join()

    def rendering_main(self):
        #self.view_lock = threading.Lock()

        # start processing thread
        self.process_data_thread = threading.Thread(target=self.process_data_loop, args=(self,),
                                                    name=self.name + 'Process_Data_Thread')
        self.process_data_thread.start()
        # wait here until thread is running
        while self.render_state.value != RENDER_RUNNING:
            time.sleep(1)

        # mainloop
        # wait here until thread is stopped
        self.render_views()

        # cleanup
        self.process_data_thread.join()
        '''self.render_state.value = RENDER_STOPPING

        count = 0
        while self.render_state.value == RENDER_STOPPING:
            if count % 20 == 0:
                logging.getLogger("sensor").debug("waiting for sensor render accept(%s) %s" % (count, self.name))
            time.sleep(0.1)
            count += 1'''
        #logging.getLogger("sensor").info("Exiting rendering_main %s" % self.name)
    
    def stop_rendering(self):
        logging.getLogger("sensor").debug("shutting down rendering thread: {0}".format(self.name))
        self.render_state.value = RENDER_STOPPING

    def wait_for_rendering_finish(self):

        logging.getLogger("sensor").debug("remove all data from queues {0}".format(self.name))

        '''# bug in multiprocessing.Queue requires shared Queues to be empty and possibly cancel_join_thread
        while not self.q_display.empty():
            self.q_display.get()
        self.q_display.cancel_join_thread()

        while not self.q_vehicle.empty():
            self.q_vehicle.get()
        self.q_vehicle.cancel_join_thread()'''

        count = 0
        while self.render_state.value > RENDER_STOPPING:
            if count % 20 == 0:
                logging.getLogger("sensor").info("waiting({1}) for rendering thread stopping: {0}".format(self.name, count))
            time.sleep(0.1)
            count += 1

        self.render_state.value = RENDER_STOPPED

    def destroy_ui(self):
        # override in subclass
        pass
        
    #@staticmethod
    #def stop(self):
    #    logging.getLogger("sensor").info("shutting down rendering thread: {0}".format(self.name))
    #    if self.process_data_thread != None:
    #        self.process_data_thread.stop()
    #    else:
    #        logging.getLogger("sensor").info("no thread: {0}".format(self.name))

    def set_window_coordinates(self, window_settings):
        if self.name in window_settings:
            coords = window_settings[self.name]
            self.window_x_position = coords['x']
            self.window_y_position = coords['y']
    
    def set_window_position(self, name, window_settings):
        if name in window_settings:
            coords = window_settings[name]
            self.window_x_position = coords['x']
            self.window_y_position = coords['y']

    def save_window_settings(self, name=None):
        if(name):
            self.name = name
        BaseSensorUI.Window_Settings_Lock.acquire()
        current_settings = {}
        if os.path.exists('window_settings.json'):
            with open('window_settings.json') as data_file:
                current_settings = json.load(data_file)
        current_settings[self.name] = {
            'x': self.window_x_position,
            'y': self.window_y_position
        }
        with open('window_settings.json', 'w') as outfile:
            json.dump(current_settings, outfile)
        BaseSensorUI.Window_Settings_Lock.release()

    def window_configure_event(self, event):
        """ Event that fires when the window changes position. """
        if self.previous_event is not None:
            if self.previous_event.x == event.x and self.previous_event.y == event.y:
                return

        self.previous_event = event

        # print("window_configure_event({0},{1}) -> ({2},{3}) - {4}".format(self.window_x_position,
        #                                                                   self.window_y_position, event.x, event.y,
        #                                                                   self.name))
        if self.view_changing_timer is not None or event.x != self.window_x_position or event.y != self.window_y_position:

            self.view_lock.acquire()
            if self.view_changing_timer is not None:
                self.view_changing_timer.cancel()
            self.view_changing_timer = threading.Timer(.5, self.window_position_changed, args=(event,))
            self.view_changing_timer.start()
            self.view_lock.release()

    def window_position_changed(self, event):
        # print("window_position_changed({0},{1}) -> ({2},{3}) - {4}".format(self.window_x_position, self.window_y_position, event.x, event.y, self.name))
        self.view_lock.acquire()
        self.view_changing_timer.cancel()
        self.view_changing_timer = None
        self.view_lock.release()
        if event.x != self.window_x_position or event.y != self.window_y_position:
            if hasattr(self, 'window_x_position'):
                self.window_x_position = event.x
            if hasattr(self, 'window_y_position'):
                self.window_y_position = event.y
            self.previous_event = None
            self.save_window_settings()

    @property
    def window_configuration_coordinates(self):
        return str(self.window_x_position) + '+' + str(self.window_y_position)

    # Render thread entry point
    @staticmethod
    def process_data_loop(sensor):
        prctl.set_proctitle("mono{0}".format(sensor))
        sensor.render_state.value = RENDER_RUNNING

        # wait here until thread stops
        while sensor.render_state.value == RENDER_RUNNING:
            sensor.process_display_data()

        # after thread stops
        logging.getLogger("sensor").debug("exiting process_data_loop {0}".format(sensor.name))
        sensor.destroy_ui()
        sensor.render_state.value = RENDER_STOPPED
        logging.getLogger("sensor").debug("done process_data_loop {0}".format(sensor.name))

    def get_display_message(self):
        data = None
        while self.render_state.value == RENDER_RUNNING:
            try:
                data = self.q_display.get(True, 1.0)
                break
            except Exception as e:
                #TODO figure oot why this is happing all the time
                #logging.getLogger("sensor").warning("get_display_message timeout {0} {1}".format(self.name, e))
                pass

        # logging.getLogger("sensor").debug("get_display_message has_data %s %s" % (data is not None, self.name))
        return data


class MatplotlibSensorUI(BaseSensorUI):
    def __init__(self, **kwargs):
        super(MatplotlibSensorUI, self).__init__(**kwargs)
        self.animation = None
        self.main_plot = None

    def initialize_views(self):
        self.main_plot = plt.figure(10)
        plt.get_current_fig_manager().window.bind('<Configure>', self.window_configure_event)
        geometry = "+" + self.window_configuration_coordinates
        plt.get_current_fig_manager().window.wm_geometry(geometry)

    def render_views(self):
        self.animation = FuncAnimation(self.main_plot, self.update_views, interval=100)
        plt.show(blocking = None)

    def update_views(self, frame):
        return


class TkinterSensorUI(BaseSensorUI):

    def __init__(self, name=None, q_display=None, **kwargs):
        super(TkinterSensorUI, self).__init__(name=None, q_display=None, **kwargs)
        self.master_tk = None
        if name != None:
            self.name = name
        if q_display != None:
            self.q_display = q_display

    def initialize_views(self):
        print("initialize view {0}".format(self.name))
        self.master_tk = tk.Tk()
        
        geometry = "300x200+" + self.window_configuration_coordinates
        self.master_tk.geometry(geometry)
        if hasattr(self, 'name'):
            self.master_tk.title(self.name)
        self.master_tk.bind('<Configure>', self.window_configure_event)

    def render_views(self):
        print("render views {0}".format(self.name))
        self.master_tk.mainloop()

    def destroy_ui(self):
        logging.getLogger("sensor").info("*** destroy ui {0}".format(self.name))
        if self.master_tk is not None:
            self.master_tk.focus_set()
            self.master_tk.quit()


    def window_configure_event(self, event):
        """ Event that fires when the window changes position. """
        event = tk.Event()
        event.x = self.master_tk.winfo_x()
        event.y = self.master_tk.winfo_y()
        super(TkinterSensorUI, self).window_configure_event(event)

import wx
class WxPythonUI(wx.App):
    def OnInit(self):
        frame = SensorGUIFrame(None, "Simple sensor frame")
        self.SetTopWindow(frame)

        frame.Show(True)
        return True

class SensorGUIFrame(wx.Frame):
    
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title, pos=(150,150), size=(350, 200))

        panel = wx.Panel(self)
        text = wx.StaticText(panel, -1, "Hello Sensor View")
        text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        text.SetSize(text.GetBestSize())

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, 0, wx.ALL, 10)

        panel.SetSizer(sizer)
        panel.Layout()