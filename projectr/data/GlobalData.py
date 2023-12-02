class GlobalData:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(GlobalData, cls).__new__(cls)
            cls._instance.data = {"start_date": "", "end_date": "", "granularity": "", "data_types": ""}
        return cls._instance

    def set_value(self, key, value):
        self.data[key] = value

    def get_value(self, key):
        return self.data.get(key)

    def check_values(self):
        return all(value != "" for value in self.data.values())
