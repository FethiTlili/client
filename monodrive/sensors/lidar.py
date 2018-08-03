
__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

from multiprocessing import Queue
import socket
import logging

from monodrive.constants import VELOVIEW_PORT, VELOVIEW_IP
from . import BaseSensor
from .gui import BaseSensorUI


class Lidar(BaseSensorUI, BaseSensor):
    def __init__(self, idx, config, simulator_config, **kwargs):
        super(Lidar, self).__init__(idx=idx, config=config, simulator_config=simulator_config, **kwargs)

        self.forwarder = None
        self.drop_frames = False
        channels_per_block = 32
        blocks_per_packet = 12
        number_blocks = 360 / config['horizontal_resolution'] * config['n_lasers'] / channels_per_block
        number_packets =  number_blocks / blocks_per_packet
        self.packet_size = int(number_blocks * 1248.0)
        self.veloview_socket = self.connect()
        self.frame_buffer = []
        self.expected_frames_per_step = number_packets

    @classmethod
    def init_display_queue(cls):
        return Queue()

    @classmethod
    def init_vehicle_queue(cls):
        return Queue()

    def digest_frame(self, frame, time_stamp, game_time):
        self.frame_buffer.append(frame)
        if len(self.frame_buffer) == self.expected_frames_per_step:
            temp_buffer = self.frame_buffer
            self.frame_buffer = []
            super(Lidar, self).digest_frame(temp_buffer, time_stamp, game_time)

    def process_display_data(self):
        data_buffer = self.get_display_message()
        if data_buffer is not None:
            for data in data_buffer:
                self.veloview_socket.sendto(data, (VELOVIEW_IP, VELOVIEW_PORT))
        self.update_sensors_got_data_count()

    def connect(self):
        """ Setup connection to the socket listening in Unreal. """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(20)
            #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.veloview_socket = s
            return s

        except socket.timeout:
            logging.getLogger("sensor").info("closing veloview_socket %s" % self.name)
            self.veloview_socket.close()
            self.veloview_socket = None

        except Exception as e:
            print('Can send to {0}'.format(str((VELOVIEW_PORT, VELOVIEW_PORT))))
            print("Error {0}".format(e))
            
            self.veloview_socket = None
            return None
    
    def destroy_ui(self):

        #rendinger is veloview so we just shut down the udp socket
        if self.veloview_socket is not None:
            try:
                #self.send_stop_stream_command(simulator)
                logging.getLogger("sensor").info("destroy_veloview_socket %s" % self.name)
                #next line is for tcp only
                #self.veloview_socket.shutdown(socket.SHUT_WR)
                self.veloview_socket.close()
            finally:
                self.veloview_socket = None
            
