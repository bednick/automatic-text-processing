import json

from dawg import RecordDAWG

filename = './data/odict.csv'

with open(filename, 'r', encoding='utf-8') as fp:
    data = fp.read().splitlines()


def get_stem(norm, forms):
    if not forms:
        return norm

    last = 0
    for i in range(len(norm)):
        if not all(norm[0:i + 1] in form for form in forms):
            break
        last = i + 1
    return norm[:last]


def split(word: str, stem: str):
    start = word.find(stem)
    finish = start + len(stem)
    return word[:start], word[finish:]


def get_index(obj, list_objs: list):
    if obj not in list_objs:
        list_objs.append(obj)
    return list_objs.index(obj)


ALL_PREFIXES = []
ALL_SUFFIXES = []
ALL_TAGS = []

ALL_SCHEMES = []

ALL_MAP = []

for i, line in enumerate(data):
    if i % 100 == 0:
        print(i / len(data))

    line_split = line.split(',')
    norm, ps, forms = line_split[0], line_split[1], list(set(line_split[2:]))
    stem = get_stem(norm, forms)

    prefixes = []
    suffixes = []
    tags = []

    all_forms = [norm] + forms
    for form in all_forms:
        pr, sf = split(form, stem)

        prefixes.append(get_index(pr, ALL_PREFIXES))
        suffixes.append(get_index(sf, ALL_SUFFIXES))
        tags.append(get_index(ps, ALL_TAGS))
    # scheme = array.array('H', prefixes + suffixes + tags)
    scheme = prefixes + suffixes + tags
    if scheme not in ALL_SCHEMES:
        ALL_SCHEMES.append(scheme)
    scheme_id = ALL_SCHEMES.index(scheme)

    for i, form in enumerate(all_forms):
        ALL_MAP.append((form, (scheme_id, i)))

record_dawg = RecordDAWG(u">II", ALL_MAP)
record_dawg.save('words.dawg')

with open('ALL_PREFIXES.json', 'w', encoding='utf-8') as fp:
    json.dump(ALL_PREFIXES, fp, ensure_ascii=False)

with open('ALL_SUFFIXES.json', 'w', encoding='utf-8') as fp:
    json.dump(ALL_SUFFIXES, fp, ensure_ascii=False)

with open('ALL_TAGS.json', 'w', encoding='utf-8') as fp:
    json.dump(ALL_TAGS, fp, ensure_ascii=False)

with open('ALL_SCHEMES.json', 'w', encoding='utf-8') as fp:
    json.dump(ALL_SCHEMES, fp, ensure_ascii=False)
