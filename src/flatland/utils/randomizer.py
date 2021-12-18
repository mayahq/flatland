import random


class BaseRandomVar:
    def __init__(self, **kwargs) -> None:
        self._set_params(**kwargs)

    def _set_params(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)
        for k, v in self.__dict__.items():
            if isinstance(v, BaseRandomVar):
                v._reset_value()
        self._reset_value()

    def _reset_value(self) -> None:
        self.value = None

    def _prettify(self) -> str:
        # return a prettier form of self.value
        return str(self.value)

    def __call__(self, pretty=False) -> str:
        self._reset_value()
        if pretty:
            return self._prettify()
        return self.value


class RandomInt(BaseRandomVar):
    def __init__(self, min=0, max=5):
        super().__init__(min=min, max=max)

    def _reset_value(self):
        self.value = random.randrange(self.min, self.max)


class RandomFloat(BaseRandomVar):
    def __init__(self, min=0.0, max=1.0):
        super().__init__(min=min, max=max)

    def _reset_value(self):
        self.value = random.uniform(self.min, self.max)


class RandomChoice(BaseRandomVar):
    def __init__(self, *choices):
        super().__init__(choices=choices)

    def _reset_value(self):
        self.value = random.choice(self.choices)


class RandomBool(BaseRandomVar):
    def __init__(self, true_prob=0.9):
        super().__init__(true_prob=true_prob)

    def _reset_value(self):
        if random.random() < self.true_prob:
            self.value = True
        else:
            self.value = False


def get_randomizer(*vals):
    func_lookup = {
        "bool": RandomBool,
        "int": RandomInt,
        "float": RandomFloat,
        "choice": RandomChoice,
    }
    if len(vals) == 1:
        vals = vals[0]
    rtype, params = vals
    if not isinstance(params, list):
        params = [params]
    rstuff = func_lookup[rtype](*params)
    return rstuff
