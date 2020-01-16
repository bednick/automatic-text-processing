from typing import Union, Set, Dict, Sequence, Optional

from pymorphy2 import MorphAnalyzer

__all__ = [
    'MorphObject',
    'SemanticObject',
    'Synonyms',
    'PartWhole',
    'GeneralPrivate',
    'SemanticVocabulary',
]

morph = MorphAnalyzer()


class MorphObject:

    def __init__(self, phrase: str, normal_form: Optional[str]):
        self.phrase = phrase
        self.normal_form = normal_form
        self.parents = set()

    @classmethod
    def parse(cls, value: Union[str, 'MorphObject']) -> 'MorphObject':
        if isinstance(value, cls):
            return value
        normal_form = '_'.join([morph.parse(word.lower())[0].normal_form for word in value.split(' ') if word])
        return cls(value, normal_form)

    def add_parent(self, parent: 'SemanticObject'):
        self.parents.add(parent)

    def __str__(self):
        return f'{self.__class__.__name__}: "{self.phrase}"'

    def __repr__(self):
        return f'<{str(self)}>'

    def __hash__(self):
        return hash(self.phrase)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.phrase == other or self.normal_form == other
        return self.phrase == other.phrase or self.normal_form == other.normal_form


class SemanticObject:

    def __init__(self, semantic_class: str, followers: Set[Union[str, 'SemanticObject']] = None,
                 values: Set[str] = None):
        self.semantic_class = semantic_class
        self.followers = followers or set()
        self._values = {MorphObject.parse(phrase) for phrase in values} if values else set()
        self.parents = set()

    def add_parent(self, parent: 'SemanticObject'):
        self.parents.add(parent)

    def __str__(self):
        return f'{self.__class__.__name__}: "{self.semantic_class}"'

    def __repr__(self):
        return f'<{str(self)}>\n'

    def __hash__(self):
        return hash(self.semantic_class)

    # @staticmethod
    # def normalize(value: str):
    #     words = value.split(' ')

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
        all_morph_objects = dict()  # type: Dict[str, MorphObject]
        all_semantic_objects = dict()  # type: Dict[str, SemanticObject]

        def build(obj: Union[str, MorphObject, SemanticObject], parent: Optional[SemanticObject]) -> Union[MorphObject, SemanticObject]:
            if isinstance(obj, str):
                obj = MorphObject.parse(obj)

            if isinstance(obj, MorphObject):
                if obj not in all_morph_objects:
                    all_morph_objects[obj.normal_form] = obj
                obj = all_morph_objects[obj.normal_form]

            elif isinstance(obj, SemanticObject):
                if obj.semantic_class not in all_semantic_objects:
                    all_semantic_objects[obj.semantic_class] = obj
                    obj.followers = [build(follower, obj) for follower in obj.followers]
                else:
                    obj = all_semantic_objects[obj.semantic_class]
            if parent:
                obj.add_parent(parent)
            return obj

        self.information = [build(info, None) for info in information]
        self.all_semantic_objects = {}  # type: Dict[MorphObject, set]
        for _, obj in all_semantic_objects.items():
            for value in obj.values():
                self.all_semantic_objects.setdefault(value, set()).add(obj)
                # if value.normal_form not in all_morph_objects:
                #     all_morph_objects[value.normal_form] = value

        self.all_morph_objects = all_morph_objects

    def search_semantic_object(self, phrase: str) -> Set[SemanticObject]:
        return self.all_semantic_objects.get(MorphObject.parse(phrase), set())

    def search_morph_object(self, phrase: str) -> Optional[MorphObject]:
        normal_form = MorphObject.parse(phrase).normal_form
        return self.all_morph_objects.get(normal_form)
