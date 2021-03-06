import json
import random


def GENERATE_NODEID():
    return "{:08x}.fed{:05x}".format(
        random.randrange(16 ** 8),
        random.randrange(16 ** 5),
    )


def GENERATE_FILEID():
    return "{:06x}-{:04x}".format(
        random.randrange(16 ** 6),
        random.randrange(16 ** 4),
    )


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

    def to_dict(self):
        return {"type": "<unk>"}

    def __str__(self):
        return json.dumps(self.to_dict())


class RandomInt(BaseRandomVar):
    def __init__(self, min=0, max=5):
        super().__init__(min=min, max=max)

    def _reset_value(self):
        self.value = random.randrange(self.min, self.max)

    def to_dict(self):
        answer = dict(type="int", min=self.min, max=self.max)
        return answer


class RandomFloat(BaseRandomVar):
    def __init__(self, min=0.0, max=1.0):
        super().__init__(min=min, max=max)

    def _reset_value(self):
        self.value = random.uniform(self.min, self.max)

    def to_dict(self):
        answer = dict(type="float", min=self.min, max=self.max)
        return answer


class RandomChoice(BaseRandomVar):
    def __init__(self, *choices):
        super().__init__(choices=choices)

    def _reset_value(self):
        self.value = random.choice(self.choices)

    def to_dict(self):
        answer = dict(type="choice", choices=self.choices)
        return answer


class RandomBool(BaseRandomVar):
    def __init__(self, true_prob=0.9):
        super().__init__(true_prob=true_prob)

    def _reset_value(self):
        if random.random() < self.true_prob:
            self.value = True
        else:
            self.value = False

    def to_dict(self):
        answer = dict(type="bool", true_prob=self.true_prob)
        return answer


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
