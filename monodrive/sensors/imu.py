
__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

import struct
import threading
import time
import logging

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import Queue
import multiprocessing
from . import BaseSensor
#from .gui import TkinterSensorUI
#from .gui import MatplotlibSensorUI
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

class IMU(BaseSensor):
    def __init__(self, idx, config, simulator_config, **kwargs):
        super(IMU, self).__init__(idx=idx, config=config, simulator_config=simulator_config, **kwargs)
        self.framing = None
        self.acceleration_vector = None
        self.angular_velocity_vector = None
        self.timer = None
        #GUI
        self.view_lock = threading.Lock()
        self.animation = None
        self.fig = None
        self.ax = None
        self.x = []
        self.y = []
        self.counter = 0
        
        
        #self.start_data_processing()
        #self.render_views()

    def run(self):
        print("super run IMU")
        self.fig, self.ax = plt.subplots()
        print(threading.current_thread())
        print(multiprocessing.current_process())
        
        #plt.show(block = None)
        
        #self.start_data_processing()
        #self.render_views()
        super(IMU, self).run()
        #self.start_data_processing()
        print("super run IMU complete")
        #self.render_views()      
        
    
    def destroy_ui(self):
        logging.getLogger("sensor").info("*** destroy ui {0}".format(self.name))
        self.running_ui = False

    @classmethod
    def parse_frame(cls, frame, time_stamp, game_time):
        print("parse IMU frame")
        print(threading.current_thread())
        print(multiprocessing.current_process())
        fmt = '=ffffffih'
        accel_x, accel_y, accel_z, ang_rate_x, ang_rate_y, ang_rate_z, timer, check_sum = list(
            struct.unpack(fmt, frame[1:31]))
        acceleration_vector = [accel_x, accel_y, accel_z]
        angular_velocity_vector = [ang_rate_x, ang_rate_y, ang_rate_z]
        data_dict = {
            'time_stamp': time_stamp,
            'game_time': game_time,
            'acceleration_vector': acceleration_vector,
            'angular_velocity_vector': angular_velocity_vector,
            'timer': timer
        }
        return data_dict
    
    
    def display(self, frame):
        self.view_lock.acquire()

        print("display for IMU")
        self.counter = self.counter + 1
        self.x.append(self.counter)
        self.y.append(self.counter)
        self.ax.plot(self.x, self.y, 'ro')
        self.fig.canvas.draw()
        self.view_lock.release()
        

    #def rendering_main(self):
    def start_data_processing(self):
        # start processing thread
        self.process_data_thread = threading.Thread(target=self.process_display_data(),
                                                    name=self.name + 'Process_Data_Thread')
        self.process_data_thread.start()

    def initialize_views(self):
        print("initialize IMU views")
        #self.view_lock.acquire()
        self.initialize_views()
        '''self.ui.main_plot.suptitle('IMU Data')
        self.ui.main_plot.set_size_inches(12.75,8.25)
        self.IMU_subplot = self.ui.main_plot.add_subplot(121)
        self.imu_table_subplot = self.ui.main_plot.add_subplot(122)
        self.imu_table_subplot.set_title('Acceration Values')
        self.imu_table_subplot.axis('tight')
        self.imu_table_subplot.axis('off')'''
        #self.view_lock.release()

    def process_display_data(self):
        print("IMU process_display_data started")
        while True:
            print("IMU process_display_data")
            print(threading.current_thread())
            print(multiprocessing.current_process())
            data = None
            try:
                data = self.q_display.peek(False, 1.0)
            except Queue.Empty:
                print("IMU Data Queue is empty")
                pass
            if data is not None:
                print("IMU GOT DATA")
                #self.view_lock.acquire()  
                #self.view_lock.release()
            time.sleep(.5)




    #def set_window_coordinates(self, window_settings):
    #    self.set_window_coordinates(window_settings)

    #def save_window_settings(self):
    #    self.save_window_settings()



class IMU1(BaseSensor):
    def __init__(self, idx, config, simulator_config, **kwargs):
        super(IMU, self).__init__(idx=idx, config=config, simulator_config=simulator_config, **kwargs)
        self.framing = None
        self.acceleration_vector = None
        self.angular_velocity_vector = None
        self.timer = None
        #GUI
        self.ui = TkinterSensorUI(self.name, self.q_display)
        self.view_lock = self.ui.view_lock

    @classmethod
    def parse_frame(cls, frame, time_stamp, game_time):
        print("parse IMU frame")
        fmt = '=ffffffih'
        accel_x, accel_y, accel_z, ang_rate_x, ang_rate_y, ang_rate_z, timer, check_sum = list(
            struct.unpack(fmt, frame[1:31]))
        acceleration_vector = [accel_x, accel_y, accel_z]
        angular_velocity_vector = [ang_rate_x, ang_rate_y, ang_rate_z]
        data_dict = {
            'time_stamp': time_stamp,
            'game_time': game_time,
            'acceleration_vector': acceleration_vector,
            'angular_velocity_vector': angular_velocity_vector,
            'timer': timer
        }
        return data_dict

    #GUI
    def initialize_views(self):
        self.ui.view_lock.acquire()
        print("initialize IMU views")
        #self.ui.view_lock.acquire()
        #super(IMU, self).initialize_views()
        #self.ui.initialize_views()

        self.ui.initialize_views()
        self.string_accel_x = tk.StringVar()
        self.accel_x_text_display = tk.Label(self.ui.master_tk, textvariable=self.string_accel_x)
        self.accel_x_text_display.pack()

        self.string_accel_y = tk.StringVar()
        self.accel_y_text_display = tk.Label(self.ui.master_tk, textvariable=self.string_accel_y)
        self.accel_y_text_display.pack()

        self.string_accel_z = tk.StringVar()
        self.accel_z_text_display = tk.Label(self.ui.master_tk, textvariable=self.string_accel_z)
        self.accel_z_text_display.pack()

        self.string_ang_rate_x = tk.StringVar()
        self.ang_rate_x_text_display = tk.Label(self.ui.master_tk, textvariable=self.string_ang_rate_x)
        self.ang_rate_x_text_display.pack()

        self.string_ang_rate_y = tk.StringVar()
        self.ang_rate_y_text_display = tk.Label(self.ui.master_tk, textvariable=self.string_ang_rate_y)
        self.ang_rate_y_text_display.pack()

        self.string_ang_rate_z = tk.StringVar()
        self.ang_rate_z_text_display = tk.Label(self.ui.master_tk, textvariable=self.string_ang_rate_z)
        self.ang_rate_z_text_display.pack()

        self.string_timer = tk.StringVar()
        self.timer_text_display = tk.Label(self.ui.master_tk, textvariable=self.string_timer)
        self.timer_text_display.pack()

        
        self.ui.view_lock.release()

    def render(self):
        try:
            #data = self.ui.get_display_message()
            print("process IMU display data")
            data = self.q_display.peek(block=False)

        except:
            pass
            #self.ui.master_tk.after(500, self.process_display_data)
            #return

        if data is not None:
            #self.ui.view_lock.acquire()
            self.string_accel_x.set('ACCEL_X: {0}'.format(data['acceleration_vector'][0]))
            self.string_accel_y.set('ACCEL_Y: {0}'.format(data['acceleration_vector'][1]))
            self.string_accel_z.set('ACCEL_Z: {0}'.format(data['acceleration_vector'][2]))
            self.string_ang_rate_x.set('ANG RATE X: {0}'.format(data['angular_velocity_vector'][0]))
            self.string_ang_rate_y.set('ANG RATE Y: {0}'.format(data['angular_velocity_vector'][1]))
            self.string_ang_rate_z.set('ANG RATE X: {0}'.format(data['angular_velocity_vector'][2]))
            self.string_timer.set('TIMESTAMP: {0}'.format(data['time_stamp']))
        else:
            print("imu data was none")
        #self.update_sensors_got_data_count()  
        self.ui.master_tk.update()
        self.ui.master_tk.after(1000, self.render)
    
    def set_window_coordinates(self, window_settings):
        self.ui.set_window_coordinates(window_settings)

    def save_window_settings(self):
        self.ui.save_window_settings()

    def start_rendering(self):
          # start processing thread
        print("IMU Start Rendering")
        #self.ui.view_lock = threading.Lock()
        self.initialize_views()
        self.ui.master_tk.after(0, self.render)
        self.ui.master_tk.mainloop()
        

