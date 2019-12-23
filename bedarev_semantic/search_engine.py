import itertools
import logging
import re
from typing import Set, List, Tuple

from pymorphy2 import MorphAnalyzer
from sklearn.feature_extraction.text import CountVectorizer

from .base import SemanticVocabulary
from .weighing import WeighingAlgorithm

__all__ = [
    'SearchEngine',
]
DELIMITERS = (',', '.', '!', '?', ':', ';')
morph = MorphAnalyzer()
logger = logging.getLogger(__package__)


class SearchEngine:
    def __init__(self, corpus: List[str], all_forms: Set[str], semantic_vocabulary: SemanticVocabulary):
        self.corpus = corpus
        self.all_forms = all_forms
        self.semantic_vocabulary = semantic_vocabulary
        self.normalize_lines_with_grams = [self.get_n_grams_from_sequence(line)
                                           for line in (self.normalize_line(doc) for doc in corpus)]
        self.positions = []
        for normalize_line_with_grams in self.normalize_lines_with_grams:
            dict_positions = {}
            for position, phrase in normalize_line_with_grams:
                dict_positions.setdefault(phrase, []).append(position)
            self.positions.append(dict_positions)

        self.vectorizer = CountVectorizer().fit(self.all_forms)
        self.text_vectors = self.vectorizer.transform([' '.join([l[1] for l in line])
                                                       for line in self.normalize_lines_with_grams])

    def search(self, line: str, algorithm: WeighingAlgorithm, max_count: int = 10):
        norm_request = self.normalize_line(line)
        request_words = [pair[1] for pair in self.get_n_grams_from_sequence(norm_request)]
        logger.info(f'request_words: {request_words}')

        weights = {(1, phrase) for phrase in request_words}
        for phrase in request_words:
            weights |= algorithm.measure(phrase, self.semantic_vocabulary)
        logger.info(f'weights: {weights}')

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
            report.append((results[0], results[1], position_info, results[2]))

        return report

    @classmethod
    def normalize_line(cls, line: str, delimiters=DELIMITERS) -> List[List[Tuple[Tuple[int, int], Set[str]]]]:
        for delimiter in delimiters:
            line = line.replace(delimiter, '\n')
        phrases = line.split('\n')

        normalize_sequence = []
        after_start = 0
        for phrase in phrases:
            normalize_phrase = []
            while phrase:
                search = re.search(r"('?[а-яА-ЯёЁ][а-яА-ЯёЁ]*(?:-[а-яА-ЯёЁ]+)*'?)", phrase)
                if not search:
                    after_start += len(phrase)
                    break
                else:
                    start = search.start()
                    end = search.end()
                    phrase = phrase[end:]
                    word = search.group(0).lower()
                    forms = set([parse.normal_form for parse in morph.parse(word) if parse.normal_form != ' '])
                    if forms:
                        normalize_phrase.append(((start + after_start, end + after_start), forms))
                    after_start += end
            after_start += 1
            if normalize_phrase:
                normalize_sequence.append(normalize_phrase)

        return normalize_sequence

    def get_n_grams_from_phrase(self, phrase: List[Tuple[Tuple[int, int], Set[str]]]):
        result = []
        #     for borders, words in phrase:
        #         result.extend([(borders[0], (word, )) for word in words])
        if len(phrase) == 1:
            return [(phrase[0][0][0], value) for value in phrase[0][1]]

        for n in range(1, min(4, len(phrase) + 1)):
            for i in range(0, len(phrase) - n + 1):
                res = ['_'.join(value) for value in itertools.product(*[pair[1] for pair in phrase][i:i + n])]
                res = [v for v in res if v in self.all_forms]
                if res:
                    result.extend([(phrase[i][0][0], r) for r in res])

        return result

    def get_n_grams_from_sequence(self, sequence: List[List[Tuple[Tuple[int, int], Set[str]]]]):
        result = []
        for phrase in sequence:
            result.extend(self.get_n_grams_from_phrase(phrase))
        return result
