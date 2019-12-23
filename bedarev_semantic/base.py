from typing import Union, Set, Dict, Sequence

from pymorphy2 import MorphAnalyzer

__all__ = [
    'SemanticObject',
    'Synonyms',
    'PartWhole',
    'GeneralPrivate',
    'SemanticVocabulary',
]

morph = MorphAnalyzer()


class SemanticObject:

    def __init__(self, semantic_class: str, followers: Set[Union[str, 'SemanticObject']] = None,
                 values: Set[str] = None):
        self.semantic_class = semantic_class
        self.followers = followers or set()
        self._values = {'_'.join([morph.parse(word.lower())[0].normal_form for word in phrase.split(' ') if word]) for
                        phrase in values} if values else set()

    def __str__(self):
        return f'{self.__class__.__name__} {self.semantic_class}: {self._values}, -> {self.followers}'

    def __repr__(self):
        return f'<{str(self)}>\n'

    @staticmethod
    def normalize(value: str):
        words = value.split(' ')

    def values(self, deep: bool = False):
        res = set(self._values)
        if deep:
            for follower in self.followers:
                res |= follower.values(deep=True)
        return res


# Синонимы
class Synonyms(SemanticObject):
    def __init__(self, semantic_class: str, values: Set[str] = None):
        super().__init__(semantic_class, values=values)

    def __str__(self):
        return f'{self.__class__.__name__} {self.semantic_class}: {self._values}'


# Отношение Часть-целое
class PartWhole(SemanticObject):
    pass


# Отношение общее частное
class GeneralPrivate(SemanticObject):
    pass


class SemanticVocabulary:

    def __init__(self, information: Sequence[SemanticObject]):
        all_objects = dict()  # type: Dict[str, SemanticObject]

        def build(obj: Union[str, SemanticObject]):
            if isinstance(obj, str):
                return obj
            if obj.semantic_class not in all_objects:
                all_objects[obj.semantic_class] = obj
                obj.followers = [build(follower) for follower in obj.followers]
                return obj
            else:
                return all_objects[obj.semantic_class]

        self.information = [build(info) for info in information]
        self.map_objects = {}  # type: Dict[str, set]
        for _, obj in all_objects.items():
            for value in obj.values():
                self.map_objects.setdefault(value, set()).add(obj)
                # self.map_objects[value].add(obj)

        self.all_objects = all_objects

    def search(self, phrase: str) -> Set[SemanticObject]:
        return self.map_objects.get(phrase, set())

