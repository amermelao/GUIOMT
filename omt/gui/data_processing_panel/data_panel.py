from omt.gui.abstract_panel import AbstractPanel


class DataPanel(AbstractPanel):

    def __init__(self):
        super(DataPanel, self).__init__()

    def packagePath(self):
        """
        This file holds the link to the active panels.
        The structure is a dictionary, the key is the class name
        and the values is where the object is define.
        """
        altenatives = {
            "LoadDynamic" : 'omt.gui.data_processing_panel.alternatives.load_dynamic_modules',
        }

        return altenatives

    def get_name(self):
        return "Process Data"

    def update_free_run_dictionary(self, data_dic):
        for panel in self.pannels_instants:
            panel.update_free_run_dictionary(data_dic)

    def get_configurations(self):
        return_dic = {}
        for function_config in self.pannels_instants:
            print function_config.name
            print function_config.name, 'yes'
            return_dic[function_config.name] = function_config.get_source_config()
        return return_dic

    def pass_functions(self):
        return  self.pannels_instants

