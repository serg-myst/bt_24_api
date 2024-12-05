class Params:
    def __init__(self, fields: list, params: dict, start=0):
        if params:
            self.__params = {}
        self.fields = fields
        self.__params = params
        self.start = start

    def add_select(self):
        self.__params = dict((f'select[{ind}]', value) for ind, value in enumerate(self.fields))

    def add_filter(self, field: str, value: int | str):
        self.__params[f"filter[{field}]"] = value

    def add_order(self, field: str, value: int | str):
        self.__params[f"order[{field}]"] = value

    def get_params(self):
        return self.__params

    def add_pagination(self):
        self.__params["start"] = self.start


if __name__ == '__main__':
    ...
