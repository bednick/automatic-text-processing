from bedarev_analyzer import MorphAnalyzer

if __name__ == '__main__':
    morph = MorphAnalyzer()
    parsed_objects = morph.parse('стекла')

    print(type(parsed_objects), len(parsed_objects))

    for result in parsed_objects:
        print(f'word: {result.word}, normal_form: {result.normal_form}, tag: {result.tag}')
