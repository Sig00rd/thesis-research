# https://pypi.org/project/unidic/
# https://clrd.ninjal.ac.jp/unidic/faq.html

import MeCab
tagger = MeCab.Tagger()

sentence = "ゴジラはモスラと一所懸命に打ち合った。"

res = tagger.parse(sentence)

tokens = res.splitlines()
for token in tokens:
    if token == 'EOS':
        break
    token_info = token.split(",")
    name, part_of_speech = token_info[0].split("\t")
    word_category = token_info[12]
    additional_info = token_info[1:]
    print(f"token: {name} pos: {part_of_speech} category: {word_category} additional info: {additional_info}")