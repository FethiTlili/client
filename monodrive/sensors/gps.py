
__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

import numpy as np
import struct

from . import BaseSensor


class GPS(BaseSensor):
    def __init__(self, idx, config, simulator_config, **kwargs):
        super(GPS, self).__init__(idx=idx, config=config, simulator_config=simulator_config, **kwargs)
        self.framing = None
        self.forward_vector = None
        self.world_location = None
        self.speed = None

    @classmethod
    def parse_frame(cls, frame, time_stamp, game_time):
        fmt = '=chhcdddfffffffhhcch'
        preamble, MSG_POS_LLH, sensor_id, payload_length, lat, lng, elev, loc_x, loc_y, for_x, for_y, for_z, ego_yaw, speed, \
        h_ac, v_ac, sats, status, crc = list(
            struct.unpack(fmt, frame))
        forward_vector = np.array([for_x, for_y, 0.0])
        world_location = np.array([loc_x / 100.0, loc_y / 100.0, 0.0])
        data_dict = {
            'time_stamp': time_stamp,
            'game_time': game_time,
            'lat': lat,
            'lng': lng,
            'elevation': elev,
            'forward_vector': forward_vector,
            'world_location': world_location,
            'ego_yaw': ego_yaw,
            'speed': speed
        }
        return data_dict

    def process_display_data(self):
        data = self.q_display.get()
        self.world_location = data['world_location']
        self.forward_vector = data['forward_vector']
        self.string_lat.set('LAT: {0}'.format(data['lat']))
        self.string_lng.set('LNG: {0}'.format(data['lng']))
        self.string_time.set('TIMESTAMP: {0}'.format(data['time_stamp']))
        self.update_sensors_got_data_count()
