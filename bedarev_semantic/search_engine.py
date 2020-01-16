import itertools
import logging
from typing import Set, List, Tuple, Optional

from sklearn.feature_extraction.text import CountVectorizer

from .base import SemanticVocabulary, SemanticObject
from .weighing import WeighingAlgorithm
from .utils import normalize_line

__all__ = [
    'SearchEngine',
]

logger = logging.getLogger(__package__)


class SearchEngine:
    def __init__(self, corpus: List[str], all_forms: Optional[Set[str]], semantic_vocabulary: SemanticVocabulary):
        self.corpus = corpus
        self.semantic_vocabulary = semantic_vocabulary
        self.all_forms = all_forms
        self.normalize_lines_with_grams = [self.get_n_grams_from_sequence(line)
                                           for line in (normalize_line(doc) for doc in corpus)]
        if not all_forms:
            self.all_forms = set()
            for line in self.normalize_lines_with_grams:
                for (pos, phrase) in line:
                    self.all_forms.add(phrase)

        self.positions = []
        for normalize_line_with_grams in self.normalize_lines_with_grams:
            dict_positions = {}
            for position, phrase in normalize_line_with_grams:
                dict_positions.setdefault(phrase, []).append(position)
            self.positions.append(dict_positions)

        self.vectorizer = CountVectorizer().fit(self.all_forms)
        self.text_vectors = self.vectorizer.transform([' '.join([l[1] for l in line])
                                                       for line in self.normalize_lines_with_grams])

    def search(self, line: str, algorithm: WeighingAlgorithm, max_count: Optional[int] = None,
               min_value: Optional[float] = None):
        norm_request = normalize_line(line)
        request_words = [pair[1] for pair in self.get_n_grams_from_sequence(norm_request)]
        logger.info(f'request_words: {request_words}')

        weights = {(1, phrase) for phrase in request_words}
        for phrase in request_words:
            weights |= algorithm.measure(phrase, self.semantic_vocabulary)
        logger.info(f'weights: {weights}')

        return self.search_by_weights(weights, max_count=max_count, min_value=min_value)

    def get_n_grams_from_phrase(self, phrase: List[Tuple[Tuple[int, int], Set[str]]]):
        result = []
        #     for borders, words in phrase:
        #         result.extend([(borders[0], (word, )) for word in words])
        if len(phrase) == 1:
            return [(phrase[0][0][0], value) for value in phrase[0][1]]

        for n in range(1, min(4, len(phrase) + 1)):
            for i in range(0, len(phrase) - n + 1):
                res = ['_'.join(value) for value in itertools.product(*[pair[1] for pair in phrase][i:i + n])]
                if self.all_forms:
                    res = [v for v in res if v in self.all_forms]
                if res:
                    result.extend([(phrase[i][0][0], r) for r in res])

        return result

    def get_n_grams_from_sequence(self, sequence: List[List[Tuple[Tuple[int, int], Set[str]]]]):
        result = []
        for phrase in sequence:
            result.extend(self.get_n_grams_from_phrase(phrase))
        return result

    def search_by_weights(self, weights: Set[Tuple[float, str]], max_count: Optional[int] = None,
                          min_value: Optional[float] = None):
        vector_request = sum([weight * self.vectorizer.transform([phrase]) for weight, phrase in weights])
        logger.info(f'vector_request: {vector_request}')
        result = self.text_vectors * vector_request.transpose()
        results_index = [
            (i, is_search, doc)
            for i, (is_search, doc) in enumerate(zip([res[0] for res in result.toarray()], self.corpus)) if is_search
        ]
        results_index.sort(key=lambda x: x[1], reverse=True)
        if max_count:
            results_index = results_index[:max_count]

        report = []
        for results in results_index:
            line_positions = self.positions[results[0]]
            position_info = {phrase: line_positions[phrase] for _, phrase in weights if phrase in line_positions}
            if position_info:
                report.append((results[0], results[1], position_info, results[2]))

        if min_value:
            report = [r for r in report if r[1] >= min_value]
        return report

    def map(self, semantic_objects: Set[SemanticObject]):
        request_words = set()
        for semantic_object in semantic_objects:
            request_words |= semantic_object.values()

        weights = {(1, phrase.normal_form) for phrase in request_words}
        logger.info(f'weights: {weights}')

        return self.search_by_weights(weights)
