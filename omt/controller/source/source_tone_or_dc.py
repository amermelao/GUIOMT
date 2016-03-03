import socket
import telnetlib
import time

from omt.controller.source.source_thread_function import FailToConnectTelonet


class ToneDCSource(object):

    def __init__(self, config_dic):

        self.ip = config_dic['ip']
        self.port = config_dic['port']
        self.frec = config_dic['frec']
        self.power = config_dic['power']

        try:
            self.connection = telnetlib.Telnet(self.ip, self.port)# for test purpuses timeout=3)
        except socket.error, exc:
            raise FailToConnectTelonet(self.ip, self.port)

        self.connection.write('power %s dbm\r\n'% self.power)
        self.connection.write('freq %s\r\n'% str(self.frec))

    def turn_on(self):
        self.connection.write('outp on\r\n')


    def turn_off(self):
        print 'tone off'
        self.connection.write('outp off\r\n')
        time.sleep(0.1)

    def stop_source(self):
        self.connection.close()