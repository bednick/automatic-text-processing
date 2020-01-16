from enum import Enum
from typing import Set, Union

__all__ = [
    'GrammeRequest',
    'Gramme',
    'Post',
    'Animacy',
    'Aspect',
    'Case',
    'Gender',
    'Involvement',
    'Mood',
    'Number'
]


class GrammeRequest(object):

    def __init__(self, request: Union[Set[str], 'GrammeRequest']):
        if isinstance(request, GrammeRequest):
            request = set(request._request)
        self._request = request

    def __and__(self, other) -> 'GrammeRequest':
        return GrammeRequest(self._request | other.request())

    def __str__(self):
        return str(self._request)

    def __repr__(self):
        return str(self)

    def request(self):
        return self._request


class Gramme(Enum):

    def request(self) -> GrammeRequest:
        return GrammeRequest({self.value})

    def __and__(self, other) -> GrammeRequest:
        return GrammeRequest(self.request() & other.request())


class Post(Gramme):
    NULL = None
    NOUN = 'NOUN'
    ADJF = 'ADJF'
    ADJS = 'ADJS'
    COMP = 'COMP'
    VERB = 'VERB'
    INFN = 'INFN'
    PRTF = 'PRTF'
    PRTS = 'PRTS'
    GRND = 'GRND'
    NUMR = 'NUMR'
    ADVB = 'ADVB'
    NPRO = 'NPRO'
    PRED = 'PRED'
    PREP = 'PREP'
    CONJ = 'CONJ'
    PRCL = 'PRCL'
    INTJ = 'INTJ'


class Animacy(Gramme):
    NULL = None
    anim = 'anim'
    inan = 'inan'


class Aspect(Gramme):
    NULL = None
    perf = 'perf'
    impf = 'impf'


class Case(Gramme):
    NULL = None
    nomn = 'nomn'
    gent = 'gent'
    datv = 'datv'
    accs = 'accs'
    ablt = 'ablt'
    loct = 'loct'


class Gender(Gramme):
    NULL = None
    masc = 'masc'
    femn = 'femn'
    neut = 'neut'
    ms_f = 'ms-f'


class Involvement(Gramme):
    NULL = None
    incl = 'incl'
    excl = 'excl'


class Mood(Gramme):
    NULL = None
    indc = 'indc'
    impr = 'impr'


class Number(Gramme):
    NULL = None
    sing = 'sing'
    plur = 'plur'


class Person(Gramme):
    NULL = None


class Tense(Gramme):
    NULL = None


class Transitivity(Gramme):
    NULL = None


class Voice(Gramme):
    NULL = None


if __name__ == '__main__':
    print(Post.INFN & Animacy.anim & Animacy.NULL)
