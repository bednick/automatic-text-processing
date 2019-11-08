import os
import json

from typing import List, Optional
from dawg_python import RecordDAWG, DAWG

__all__ = [
    'Parse',
    'MorphAnalyzer',
]


class Parse(object):

    def __init__(self, word: str, normal_form: str, tag: Optional[str]):
        self.word = word
        self.normal_form = normal_form
        self.tag = tag

    def __str__(self):
        return f'{self.word} {self.normal_form} {self.tag}'

    def __repr__(self):
        return f'<word: "{self.word}", normal_form: "{self.normal_form}", tag: "{self.tag}">'


def _filename(name: str) -> str:
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', name)


def _load_json(name: str):
    with open(_filename(name), 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    return data


class MorphAnalyzer(object):
    ALL_SCHEMES = _load_json('ALL_SCHEMES.json')
    ALL_PREFIXES = _load_json('ALL_PREFIXES.json')
    ALL_SUFFIXES = _load_json('ALL_SUFFIXES.json')
    ALL_TAGS = _load_json('ALL_TAGS.json')
    WORDS = RecordDAWG(u">II").load(_filename('words.dawg'))
    SUBSTITUTES = DAWG.compile_replaces({'е': 'ё'})

    def __parse(self, word, scheme_id, scheme_number) -> Parse:
        scheme = self.ALL_SCHEMES[scheme_id]
        prefix = self.ALL_PREFIXES[scheme[scheme_number]]
        suffix = self.ALL_SUFFIXES[scheme[len(scheme) // 3 + scheme_number]]
        tag = self.ALL_TAGS[scheme[len(scheme) // 3 * 2 + scheme_number]]

        stem = word[len(prefix):-len(suffix)]
        return Parse(
            word,
            ''.join((self.ALL_PREFIXES[scheme[scheme_number]], stem, self.ALL_SUFFIXES[scheme[len(scheme) // 3]])),
            tag
        )

    def parse(self, word: str) -> List[Parse]:
        result = []
        for _word, schemes in self.WORDS.similar_items(word, self.SUBSTITUTES):
            result.extend([self.__parse(word, scheme_id, scheme_number) for (scheme_id, scheme_number) in schemes])
        if not result:
            result.append(Parse(word, word, None))
        return result
