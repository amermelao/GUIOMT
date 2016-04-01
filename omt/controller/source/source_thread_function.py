import telnetlib
import time
import socket

from omt.controller.abstract_parallel_proces import Process


class AbstractSource(Process):

    def is_dummy(self):
        return False

    def set_generator(self, current_channel):
        pass


class SourceThread(AbstractSource):

    def __init__(self, config_dic):
        self.ip = config_dic['ip']
        self.port = config_dic['port']

        # set the sweep configutation
        # the configuration comes from the GUI
        # and is pass in the Coordinator class
        self.frec_init = config_dic['frec_init']
        self.frec_end = config_dic['frec_end']
        self.frec_number_of_points = config_dic['frec_number_point']
        self.frec_step = (self.frec_end - self.frec_init)/(self.frec_number_of_points - 1.0)

        try:
            #self.connection = telnetlib.Telnet(self.ip, self.port,timeout=3) # for test purpuses, time in secconds
            self.connection = telnetlib.Telnet(self.ip, self.port)
        except socket.error, exc:
            raise FailToConnectTelnet(self.ip, self.port)
        self.connection.write('power ' + config_dic['power'] + ' dbm\r\n')

    def ask_a_command(self, a_command):
        self.connection.write(a_command + '?\r\n')
        response = self.connection.read_until(b"\n")
        return response

    def set_generator(self, current_channel):
        self.connection.write('freq ' + str(current_channel * self.frec_step + self.frec_init) + '\r\n')
        print 'addquiere ' + str(current_channel)
        # wait for the tone to adjust well
        time.sleep(2)

    def close_process(self):
        self.connection.close()


class DummySourceThread(AbstractSource):


    def close_process(self):
        print 'dummy stop'

    def is_dummy(self):
        return True


class FailToConnectTelnet(Exception):

    def __init__(self, ip, port):
        self.value = 'fail to conect to %s:%s'% (ip, port)