import re
from typing import Set, List, Tuple

from pymorphy2 import MorphAnalyzer

__all__ = [
    'normalize_line',
]

DELIMITERS = (',', '.', '!', '?', ':', ';')
morph = MorphAnalyzer()


def normalize_line(line: str, delimiters=DELIMITERS) -> List[List[Tuple[Tuple[int, int], Set[str]]]]:
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
