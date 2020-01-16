from typing import Sequence, Union, Tuple, Optional

from bedarev_syntax.gramme import *
from bedarev_syntax.text import Text, Sentence, Word

__all__ = [
    'search',
]


def _to_prepare(request: Sequence[Union[str, GrammeRequest]]) -> Sequence[Union[Word, GrammeRequest]]:
    result = []

    for form in request:
        if isinstance(form, str):
            sentence = Sentence.parse(form)
            result.extend(sentence.words)
        elif isinstance(form, GrammeRequest):
            result.append(form)
        else:
            raise ValueError(f'Incorrect type in request sequence: {type(form)}')

    return result


def _check(request: Union[Word, GrammeRequest], word: Word) -> bool:
    # print('CHECK\n', request, '\n', word)
    if isinstance(request, Word):
        # print('RAW', request.raw, word.raw, request.raw == word.raw)
        return request.raw == word.raw
    if isinstance(request, GrammeRequest):
        return any(request.request() in parse.tag for parse in word.parses)


def _search_in_sentence(requests: Sequence[Union[Word, GrammeRequest]], sentence: Sentence) -> Optional[Tuple[int, int]]:
    position = 0
    while position < len(sentence) - len(requests):
        start_poss = sentence[position][0]
        finish_poss = None
        for i in range(len(requests)):
            r = requests[i]
            finish_poss, w = sentence[i+position]
            if not _check(r, w):
                # print('NOT CHECK\n')
                finish_poss = None
                break

        if finish_poss is not None:
            return start_poss[0], finish_poss[1]
        position += 1


def search(requests: Sequence[Union[str, GrammeRequest]], text: Text) -> Optional[Tuple[int, int]]:
    requests = _to_prepare(requests)

    for poss_text, sentence in text:
        poss_sen = _search_in_sentence(requests, sentence)
        if poss_sen:
            return poss_text[0] + poss_sen[0], poss_text[0] + poss_sen[1]


if __name__ == '__main__':
    example_text = Text.parse('Пример текста с несколькими предложениями. А это второе предложение')
    examples_requests = [
        ['это', Post.ADJF.request()],  # "это" + "имя прилагательное"
        ['это', Post.GRND.request()],  # "это" + "деепричастие"
    ]

    print(example_text.raw)
    for example_requests in examples_requests:
        print()
        res = search(example_requests, example_text)
        print(f'SEARCH: {str(example_requests)}')
        print(f'RESULT: "{example_text.raw[max(0, res[0]-17):res[1]+12] if res else None}"')
