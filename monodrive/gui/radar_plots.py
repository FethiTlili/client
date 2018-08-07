from __future__ import print_function

import matplotlib
matplotlib.use('TkAgg')
import numpy as np

try:
    import matlab.engine
except ImportError:
    eng = None


class BaseRadarMethod:
    def setup_radar_plots(self, **kwargs):
        raise NotImplemented

    def set_data(self, **kwargs):
        raise NotImplemented

    def extents(self, f):
        delta = f[1] - f[0]
        return [f[0] - delta / 2, f[-1] + delta / 2]


class RadarMethodDetectionRootMusicAndESPRIT(BaseRadarMethod):

    def setup_radar_plots(self, subplot1, subplot2, data):
        subplot1.grid(visible=True)
        AOA_handle, = subplot1.plot(data['obstaclesA'], data['obstaclesR'],
                                    linestyle='None', marker='s', markerfacecolor = 'r', markeredgecolor = 'r')
        if len(data['obstaclesR']) > 20:  #to adjust table vertical position in the figure
            max_table_size = 27
        else:
            max_table_size = 20

        obstacles_handle = subplot2.table(cellText=data['obstacles'][0:max_table_size],
                                          colLabels=("Obstacle", "Range", "Speed", "AoA", "RCS", "Power\n level"),
                                          loc='center')
        obstacles_handle.auto_set_font_size(False)
        obstacles_handle.set_fontsize(5.5)
        for i in range(0,6):
            for j in range(len(data['obstaclesR']) + 1, max_table_size + 1):
                    obstacles_handle._cells[(j,i)]._text.set_text('')
                    obstacles_handle._cells[(j,i)].set_linewidth(0)


        self.old_size = len(data['obstaclesR'])

        return AOA_handle, obstacles_handle

    def set_data(self, handle1, handle2, data):
        obstacles = np.array([])
        if len(data):
            obstacles[0:len(data['obstaclesR']),   0] = range(0, len(data['obstaclesR']))
            obstacles[0:len(data['obstaclesR']),   1] = data['obstaclesR']
            obstacles[0:len(data['obstaclesV']),   2] = data['obstaclesV']
            obstacles[0:len(data['obstaclesA']),   3] = data['obstaclesA']
            obstacles[0:len(data['obstaclesRCS']), 4] = data['obstaclesRCS']
            obstacles[0:len(data['obstaclesPL']),  5] = data['obstaclesPL']

            handle1.set_xdata(data['obstaclesA'])
            handle1.set_ydata(data['obstaclesR'])

        for i in range(0, 6):
            for j in range(1, self.old_size + 1): #to erase previous display
                try:
                    handle2._cells[(j,i)]._text.set_text('')
                    handle2._cells[(j,i)].set_linewidth(0)
                except:
                    pass

        for i in range(0,6):
            for j in range(1, len(data['obstaclesR']) + 1): #to refresh with new display
                try:
                    handle2._cells[(j, i)]._text.set_text(obstacles[j - 1, i])
                    handle2._cells[(j, i)].set_linewidth(1)
                except:
                    pass

        self.old_size = len(data['obstaclesR'])


class RadarMethodDopplerFFT(BaseRadarMethod):

    def setup_radar_plots(self, subplot, data):
        data = np.flipud(20 * np.log10(data['rngdop']))
        vvv = self.extents(np.linspace(-data['v_max'], data['v_max'], data['n_sweep']))
        rrr = self.extents(np.linspace(data['range_max'], 0, data['NN']))

        doppler_handle = subplot.imshow(
            data, aspect='auto', interpolation='none', extent=vvv + rrr, origin='lower')
        return doppler_handle

    def set_data(self, handle, data):
        handle.set_data(data['rngdop'])


class RadarPlotAoAFFT(BaseRadarMethod):

    def setup_radar_plots(self, subplot, data):
        data = np.flipud(20 * np.log10(data['range_aoa']))
        self.vvv = self.extents(np.linspace(-data['v_max'], data['v_max'], data['n_sweep']))
        self.rrr = self.extents(np.linspace(data['range_max'], 0, data['NN']))

        AOA_handle = subplot.imshow(
            data, aspect='auto', interpolation='none', extent=self.vvv + self.rrr, origin='lower')
        return AOA_handle

    def set_data(self, handle, data):
        handle.set_data(data['range_aoa'])

