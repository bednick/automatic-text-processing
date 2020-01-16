from typing import List, Tuple

from nltk import sent_tokenize, word_tokenize
from pymorphy2 import MorphAnalyzer
from pymorphy2.analyzer import Parse
from pymorphy2.tagset import OpencorporaTag

__all__ = [
    'Text',
    'Sentence',
    'Word'
]

morph = MorphAnalyzer()


class Text(object):
    def __init__(self):
        self.raw = None  # type: str
        self.sentences = None  # type: List[Sentence]
        self.positions = None  # type: List[Tuple[int, int]]

    @classmethod
    def parse(cls, text: str) -> 'Text':
        # tokens = sent_tokenize(text, language='russian')
        tokens = sent_tokenize(text)
        self = cls()
        self.raw = text
        self.sentences = []
        self.positions = []

        offset = 0
        for token in tokens:
            start = text.index(token, offset)
            offset = start + len(token)
            self.sentences.append(Sentence.parse(token))
            self.positions.append((start, offset))

        return self

    def __str__(self):
        if self.sentences and self.positions:
            return f'{list(zip(self.positions, self.sentences))}'
        else:
            return '[]'

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.sentences) if self.sentences else 0

    def __iter__(self):
        for position, sentence in zip(self.positions, self.sentences):
            yield position, sentence

    def __getitem__(self, item):
        return self.positions[item], self.sentences[item]


class Sentence(object):
    def __init__(self):
        self.raw = None
        self.words = None  # type: List[Word]
        self.positions = None  # type: List[Tuple[int, int]]

    @classmethod
    def parse(cls, sentence: str) -> 'Sentence':
        # tokens = word_tokenize(sentence[1], language='russian')
        tokens = word_tokenize(sentence)

        self = cls()
        self.raw = sentence
        self.words = []
        self.positions = []

        offset = 0
        for token in tokens:
            try:
                start = sentence.index(token, offset)
            except ValueError:
                continue
            offset = start + len(token)
            self.words.append(Word.parse(token))
            self.positions.append((start, offset))

        return self

    def __str__(self):
        if self.words and self.positions:
            return f'{list(zip(self.positions, self.words))}'
        else:
            return '[]'

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.words) if self.words else 0

    def __iter__(self):
        for position, word in zip(self.positions, self.words):
            yield position, word

    def __getitem__(self, item):
        return self.positions[item], self.words[item]


class Word(object):
    def __init__(self):
        self.raw = None
        self.parses = None  # type: List[Parse]

    @classmethod
    def parse(cls, word) -> 'Word':
        self = cls()
        self.raw = word
        self.parses = morph.parse(word.lower())
        # self.parses = [parse for parse in self.parses if parse.normal_form != ' ']
        return self

    def __str__(self):
        return f'[{str(self.parses[0])}, {"..." if len(self.parses) > 1 else ""}]' if self.parses else '[]'

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.parses) if self.parses else 0

    def __iter__(self):
        for parse in self.parses:
            yield parse

    def __getitem__(self, item):
        return self.parses[item]


if __name__ == '__main__':
    text = Text.parse('Какой-то сложный текст. Сложные предложения')
    for _, sentence in text:
        print(sentence.raw)
        print(sentence[1:])

        # for _, word in sentence:
        #     parse = word.parses[0]  # type: Parse
        #     tag = parse.tag  # type: OpencorporaTag
        #     print(parse)
        #     print(tag)
        #
        #     break

        break
