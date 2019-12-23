from abc import ABCMeta, abstractmethod
from typing import Set
from typing import Union

from bedarev_semantic.base import *

__all__ = [
    'WeighingAlgorithm',
    'TopDownAlgorithm',
]


class WeighingAlgorithm(metaclass=ABCMeta):
    @abstractmethod
    def measure(self, phrase: str, semantic_vocabulary: SemanticVocabulary):
        pass


class TopDownAlgorithm(WeighingAlgorithm):

    def __init__(self, synonyms: float = 0.9, general_private: float = 0.5, part_whole: float = 0.25):
        self.synonyms = synonyms
        self.general_private = general_private
        self.part_whole = part_whole

    @classmethod
    def get_values(cls, obj: Union[str, SemanticObject]) -> Set[str]:
        if isinstance(obj, str):
            return {obj}
        all_values = set()
        for value in obj.values():
            all_values |= cls.get_values(value)
        return all_values

    @classmethod
    def get_values_followers(cls, obj: Union[SemanticObject]) -> Set[str]:
        all_values = set()
        for follower in obj.followers:
            if isinstance(obj, str):
                all_values.add(obj)
            else:
                all_values |= cls.get_values(follower)
        return all_values

    def measure(self, phrase: str, semantic_vocabulary: SemanticVocabulary):
        result = set()

        for search in semantic_vocabulary.search(phrase):
            if isinstance(search, Synonyms):
                result |= {(self.synonyms, v) for v in self.get_values(search) if v != phrase}
            elif isinstance(search, GeneralPrivate):
                result |= {(self.synonyms, v) for v in self.get_values(search) if v != phrase}
                result |= {(self.general_private, v) for v in self.get_values_followers(search)}
            elif isinstance(search, PartWhole):
                result |= {(self.synonyms, v) for v in self.get_values(search) if v != phrase}
                result |= {(self.part_whole, v) for v in self.get_values_followers(search)}

        return {(res[0], '_'.join(res[1].split(' '))) for res in result}
