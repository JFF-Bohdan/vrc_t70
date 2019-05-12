class SensorReadData(object):
    def __init__(
        self,
        device_address=None,
        sensor_address=None,
        trunk_number=None,
        sensor_index=None,
        is_connected=None,
        temperature=None
    ):
        self.device_address = device_address
        self.sensor_address = sensor_address
        self.trunk_number = trunk_number
        self.sensor_index = sensor_index
        self.is_connected = is_connected
        self.temperature = temperature

    def __str__(self):
        dict_data = self.__dict__
        items = []
        for k in sorted(dict_data.keys()):
            v = dict_data[k]
            items.append("{}={}".format(k, v))

        str_attrs = ",".join(items)
        return "{}({})".format(self.__class__.__name__, str_attrs)

    def __repr__(self):
        return self.__str__()
