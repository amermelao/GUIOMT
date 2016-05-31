import csv
import struct
import corr
import logging
import time

import datetime
import numpy
from Gnuplot import Gnuplot

from omt.util.data_type import data_type_dictionart


class Roach_FPGA(object):

    def __init__(self, data_dic):

        print data_dic
        try:
            self.port = int(data_dic['port'])
        except:
            raise MissingInformation('port')
        try:
            self.ip = data_dic['ip']
        except:
            raise MissingInformation('ip')
        self.register_list = data_dic['reg']
        self.bof_path = data_dic['bof_path']
        self.bitstream = str(data_dic['name'] + '.bof')
        self.brams_info = data_dic['bram']
        self.program = data_dic['progdev']

        self.plot_brams = []
        self.store_drams = []

        for cont in range(len(self.brams_info)):
            self.brams_info[cont]['prev_acc'] = 0

        for cont in range(len(self.brams_info)):
            aplot = None
            if self.brams_info[cont]['plot']:
                aplot = Gnuplot(debug=1)
                aplot.clear()
                aplot('set style data linespoints')
                aplot.ylabel('Power AU (dB)')
                aplot('set xrange [-50:2098]')
                aplot('set yrange [0:100]')
                aplot('set ytics 10')
                aplot('set xtics 256')
                aplot('set grid y')
                aplot('set grid x')
            self.plot_brams.append(aplot)

            astore = None

            if self.brams_info[cont]['store']:
                ts = time.time()
                time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                print self.brams_info[cont].keys()
                file_name = self.bof_path[:-len('.bof')] + '-' + self.brams_info[cont]['array_id'] + '-' + time_stamp + '.csv'
                file = open(file_name, 'w')

                csv_writer = csv.writer(file, delimiter = ',')
                astore = (csv_writer,file)
            self. store_drams.append(astore)

        self.fpga = None

        self.handler = corr.log_handlers.DebugLogHandler()
        self.logger = logging.getLogger(self.ip)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(10)

    def connect_to_roach(self):
        print self.port
        self.fpga = corr.katcp_wrapper.FpgaClient(self.ip, self.port, timeout=10, logger=self.logger)
        time.sleep(1)

    def is_conected(self):
        to_return = self.fpga.is_connected()
        return to_return

    def send_bof(self):
        if not self.program:
            return

    def config_register(self):
        if self.program:
            for reg_info in self.register_list:
                self.fpga.write_int(reg_info[0],int(reg_info[1]))

    def accuaire_data(self):

        if not self.is_conected():
            return {}

        return_data = {}
        bram_cont = 0

        cont_dictionary = {'':[]}

        for bram in self.brams_info:
            if bram['is_bram']:
                if not bram['acc_len_reg'] in cont_dictionary:
                    cont_dictionary[bram['acc_len_reg']] = []

                cont_dictionary[bram['acc_len_reg']].append(bram)

        # create a funcion to extract data

        function_dictionary = {}
        for acc_reg in cont_dictionary:
            func = None

            function_dictionary[acc_reg] = []

            for bram in cont_dictionary[acc_reg]:
                bram_func_real = lambda : None
                bram_func_image = lambda : None
                array_size = bram['size']
                data_type = bram['data_type']

                for names in bram['bram_names']:
                    real_name = names[0]
                    imag_name = names[1]

                    aux_function = bram_func_real

                    bram_func_real = lambda : None if len(real_name) <1 else \
                        lambda : (struct.unpack('>'+str(array_size) + data_type, self.fpga.read(real_name, str(int(array_size)*data_type_dictionart[data_type]), 0)), aux_function())

                    aux_function = bram_func_image
                    bram_func_image = lambda : None if len(real_name) <1 else \
                        lambda : (struct.unpack('>'+str(array_size) + data_type,
                                    self.fpga.read(imag_name, str(int(array_size)*data_type_dictionart[data_type]), 0)),
                                aux_function())
                function_dictionary[acc_reg].append((bram,bram_func_real,bram_func_real))

        extracted_data = []
        for reg in function_dictionary:
            for func in function_dictionary[reg]:
                lol = func[1]()
                lal = func[2]()
                extracted_data.append((func[0],lol, lal))

        return_data = {}

        for data in extracted_data:
            return_data[data] = [1]


        return_data['fpga'] = self.fpga

        return return_data

    def program_fpga(self):
        if self.program:
            self.fpga.progdev(self.bitstream)

    def stop(self):
        self.fpga.stop()

        bram_cont = 0

        for bram in self.brams_info:
            if bram['is_bram']:
                if bram['plot']:
                    self.plot_brams[bram_cont].close()

                if bram['store']:
                    files = self.store_drams[bram_cont]
                    files[1].close()
            bram_cont += 1


    def fail(self):
        return self.handler.printMessages()

    def get_fpga_instance(self):
        pass

    def extract_data_from_one_bram(self, return_data,bram,bram_cont):
        if bram['is_bram']:
            acc_len_ref = bram['acc_len_reg']
            data_type = bram['data_type']
            array_size = bram['size']
            acc_n = -1

            while (len(acc_len_ref) > 0):
                acc_n = self.fpga.read_uint(acc_len_ref)
                if acc_n > 1+bram['prev_acc']:
                    bram['prev_acc'] = acc_n
                    break

            print acc_n

            have_real = True
            have_imag = True

            real_data = []
            imag_data = []

            nbram = len(bram['bram_names'])

            for names in bram['bram_names']:
                real_name = names[0]
                imag_name = names[1]

                #print '>'+str(array_size) + data_type, real_name,str(int(array_size)*data_type_dictionart[data_type]), 0

                if len(real_name) > 0:
                    real_array = struct.unpack('>'+str(array_size) + data_type, self.fpga.read(real_name,str(int(array_size)*data_type_dictionart[data_type]), 0))
                    real_data.append(real_array)
                else:
                    have_real = have_real and False

                if len(imag_name) > 0:
                    imag_array = struct.unpack('>'+str(array_size) +
                                               data_type, self.fpga.read(imag_name,str(int(array_size)*data_type_dictionart[data_type]), 0))
                    imag_data.append(imag_array)
                else:
                    have_imag = have_imag and False

            final_array = numpy.zeros((int(array_size)*nbram),dtype=complex)

            for cont0 in range(int(array_size)):

                for cont1 in range(nbram):
                    if have_real:
                        real_part = real_data[cont1][cont0]
                    else:
                        real_part = 0

                    if have_imag:
                        imag_part = imag_data[cont1][cont0]
                    else:
                        imag_part = 0

                    final_array[cont0*nbram + cont1] = real_part + 1j*imag_part

            return_data[bram['array_id']] = (final_array, acc_n)

            if bram['plot']:
                aplot = self.plot_brams[bram_cont]
                aplot.clear()
                data = 10*numpy.log10(1.0+numpy.absolute(final_array))
                x_range = int(numpy.amax(data) * 1.1)


                if have_real and have_imag:
                    aplot('set multiplot layout 2,1 rowsfirst')
                    aplot('set yrange [0:%s]' % (str(x_range)))
                    aplot('set ytics 10')
                    aplot.plot(data)
                    aplot('set ytics 20')
                    aplot('set yrange [-181:181]')
                    aplot.plot(numpy.angle(final_array)*180/3.141592)

                    aplot('unset multiplot')
                else:
                    aplot('set yrange [0:%s]' % (str(x_range)))
                    aplot.plot(data)
                aplot.title('plot of data array %s, acc count %s'%(self.brams_info[bram_cont]['array_id'],str(acc_n)))
                #time.sleep(0.3)

            if bram['store']:
                    files = self.store_drams[bram_cont]
                    str_final = []
                    for data in final_array:
                        str_final.append('{:f}'.format(data))
                    files[0].writerow(str_final)
        else:
            if 'snap' in bram:
                return_data[bram['name']] = numpy.fromstring(self.fpga.snapshot_get(bram['name'], man_trig=True, man_valid=True)['data'], dtype='>i1')
            else:
                if bram['load_data']:
                    self.fpga.write_int(bram['reg_name'], int(bram['reg_value']))
                else:
                    return_data[bram['reg_name']] = self.fpga.read_uint(bram['reg_name'])


class DummyRoach_FPGA(Roach_FPGA):

    def __init__(self, data_dic):
        self.brams_info = data_dic['bram']

    def connect_to_roach(self):
        pass

    def is_conected(self):
        return True

    def send_bof(self):
        pass

    def config_register(self):
        pass

    def accuaire_data(self):

        if not self.is_conected():
            return {}

        return_data = {}

        for bram in self.brams_info:
            if bram['is_bram']:
                return_data[bram['array_id']] = ((-1 + 1j,-1 + 2j,-1 + 3j, 1 + 4j, 1 + 5j), -1)
            else:
                if bram['load_data']:
                    pass
                else:
                    return_data[bram['reg_name']] = 0

        return return_data


    def program_fpga(self):
        pass

    def stop(self):
        pass


class MissingInformation(Exception):

    def __init__(self, text):
        self.message = 'missing ROACH: %s'% (text)