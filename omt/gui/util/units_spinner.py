from kivy.uix.spinner import Spinner


class UnitSpinner(Spinner):

    hz = 'hz'
    db = 'dB'
    simple = 'simple'

    def __init__(self, units):

        self.units_dict = {}

        if units == 'hz':
            self.units_dict = {'nHz':10**-9,'uHz':10**-6,'mHz':10**-3,'Hz' : 1, 'KHz' : 10**3, 'MHz' : 10**6, 'GHz' : 10**9, 'THz' : 10**12}
        elif units == 'dB':
            self.units_dict = {'dBm': 'algo', 'dB':'nop'}
        elif units == 'simple':
            self.units_dict = {'n':10**(-9), 'u':10**(-6), 'm' : 10**(-3),' ' : 1, 'K' : 10**3, 'M' : 10**6, 'G' : 10**9, 'T' : 10**12}
        values = self.units_dict.keys()

        super(UnitSpinner, self).__init__(text=values[0], values=values, size_hint=(None, None), size = (35,44))

    def get_unit_norm(self):
        a_key = self.text
        return self.units_dict[a_key]

    def get_unit(self):
        return self.text

    def set_unit(self, val):
        all_key = self.units_dict.keys()

        for aKey in all_key:
            if self.units_dict[aKey] == val:
                self.text = aKey
                return