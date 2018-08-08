from __future__ import print_function

__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

import logging

import matplotlib
matplotlib.use('TkAgg')

import struct
import numpy as np
import multiprocessing

from . import BaseSensorPacketized
from monodrive.signal_processing import radar_method
#from monodrive.gui.widgets import MatplotlibSensorUI

try:
    import matlab.engine
    #eng = matlab.engine.start_matlab()
    #eng.addpath(os.path.join(BASE_PATH, 'matlab'), nargout=1)
except ImportError:
    eng = None


class Radar(BaseSensorPacketized):
    def __init__(self, idx, config, simulator_config, **kwargs):
        super(Radar, self).__init__(idx=idx, config=config, simulator_config=simulator_config, **kwargs)
        self.framing = None
        self.ncores = multiprocessing.cpu_count()
        #self.N = config['num_samples_per_sweep']
        C = 3e8
        Tm = config['sweep_num_for_range_max']* 2 * config['range_max']/ C
        self.N = int(round(config['fs']* Tm))
        self.N_Clean = int(self.N)
        self.nSweep = int(config['num_sweeps'])
        self.n_rx_elements = 8
        self.v_max = 30
        self.bounding_box = None
        #self.radar_plot = None
        self.radar_signals = None
        self.xr_dechirped = None
        self.xr_doppler = None

        self.axs = None
        self.last_data_frame_processed = True

        self.bounding_angles = []
        self.bounding_distances = []

        #Set Your Method of Radar Processing Here
        self.radar_method = radar_method.RadarMethodDetectionRootMusicAndESPRIT(config, self.ncores)
        # self.radar_method_doppler = RadarMethod.RadarMethodDopplerFFT(config, self.ncores)
        # self.radar_method_aoa = RadarMethod.RadarMethodAoAESPRIT(config, self.ncores)
        #self.radar_method_aoa = RadarMethod.RadarMethodAoAFFT(config, self.ncores)

    def get_frame_size(self):
        return self.N * 32 * 2 * self.n_rx_elements * self.nSweep / 8

    @classmethod
    def parse_frame(cls, frame, time_stamp, game_time):
        print('Radar     : parse frame: %d, %d' % (time_stamp, game_time))
        return {
            'game_time': game_time,
            'time_stamp': time_stamp,
            'data': frame
        }

    def get_message(self):
        print('%s: get_message' % self.name)
        data = self.q_data.peek()
        data.update(self.process_radar_data_cube(data['data']))
        print('%s: data=%s' % (self.name, str(data.keys())))
        print('            obstacles=%d' % len(data['obstaclesR']))
        return data

    def process_radar_data_cube(self, data):
        numberOfItems = self.N * self.n_rx_elements * self.nSweep * 2
        try:
            s_data = struct.unpack('f' * int(numberOfItems), data)
        except:
            logging.getLogger("sensor").error("Could not unpack radar data")
            s_data = []

        result = {
            'n_sweeps': self.nSweep,
            'v_max': self.v_max
        }

        if len(s_data) == numberOfItems:
            r = np.array(s_data[::2])
            i = np.array(s_data[1::2])
            sf = np.array(r + 1j * i, dtype=complex)
            xr = sf.reshape((self.nSweep, self.n_rx_elements, self.N))
            self.xr_dechirped = np.real(xr[int(self.nSweep / 2), 0, :])
            self.xr_doppler = np.real(xr[:, 0, int(self.N / 2)])

            han = np.hanning(1024)
            han = np.transpose(han)
            hannMat = np.tile(han, (self.nSweep, 1))
            hannMat = np.transpose(hannMat)

            hannMat_aoa = np.tile(han, (self.n_rx_elements, 1))
            hannMat_aoa = np.transpose(hannMat_aoa)

            result.update(self.radar_method.process_radar_data_cube(xr, hannMat_aoa, hannMat))
            # self.radar_method_aoa.process_radar_data_cube(xr, hannMat_aoa,hannMat)
            self.last_data_frame_processed = True
        else:
            #print("len(s_data) != numberOfItems")
            pass

        return result

