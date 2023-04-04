# http://jhlee.sakura.ne.jp/papers/lee-et-al2016rb.pdf
# https://pypi.org/project/unidic/
# https://clrd.ninjal.ac.jp/unidic/faq.html
# https://japanese.stackexchange.com/a/63365
# https://jreadability.net/sys/ja

# one note: Lee is using  MeCab v0.996 amd UniDic v2.2.0

import MeCab

import pickle
import re
from typing import Dict, List

from character_type import get_char_type, LETTER_TYPES, SENTENCE_ENDING_CHARACTER_TYPES
from readability_factor import ReadabilityFactor


WAGO_TAG = "和"  # thing to consider: mecab is tagging '行っ' as wago - is that correct?
KANGO_TAG = "漢"
VERB_TAG = "動詞"
# https://japanese.stackexchange.com/a/63365 states that 補助動詞 (subsidiary verbs - teoku, teiru etc.)
# are sometimes called auxiliary as well;
# mecab /w unidic doesn't seem to categorize anything as 補助動詞 though;
# eg. teiru is broken into te (particle) + iru (verb)
AUXILIARY_VERB_TAG = "助動詞"

MEAN_SENTENCE_LENGTH = "MEAN SENTENCE LENGTH"
KANGO_PROPORTION = "KANGO PROPORTION"
WAGO_PROPORTION = "WAGO PROPORTION"
VERB_PROPORTION = "VERB PROPORTION"
AUXILIARY_VERB_PROPORTION = "AUXILIARY VERB PROPORTION"
CONSTANT = "CONSTANT"

WEIGHTS = {
    MEAN_SENTENCE_LENGTH: -0.056,  # calculate as in tateisi formula
    KANGO_PROPORTION: -0.126,  # assuming proportion to all tokens since Lee doesn't specify what does he mean by word
    WAGO_PROPORTION: -0.042,
    VERB_PROPORTION: -0.145,
    AUXILIARY_VERB_PROPORTION: -0.044,
    CONSTANT: 11.724,
}


class LeeReadabilityFormula:
    def __init__(self) -> None:
        self.tagger = MeCab.Tagger()
        self.readability_factors: Dict[str, float] = {
            MEAN_SENTENCE_LENGTH: 0.0,
            KANGO_PROPORTION: 0.0,
            WAGO_PROPORTION: 0.0,
            VERB_PROPORTION: 0.0,
            AUXILIARY_VERB_PROPORTION: 0.0,
            CONSTANT: 1,
        }
        self.sentence_lengths: List[int] = []
        self.all_tokens_count = 0
        self.kango_count = 0
        self.wago_count = 0
        self.verb_count = 0
        self.auxiliary_verbs_count = 0

    def parse_text(self, text: str) -> None:
        sentences: List[str] = []
        lines = list(filter(lambda x: x != "", text.splitlines()))

        for line in lines:
            line_sentences = re.split(r"」|。", line)
            for sentence in line_sentences:
                if len(sentence):
                    sentences.append(sentence)
        for sentence in sentences:
            self.parse_sentence_and_print_results(sentence)

    def parse_sentence_and_print_results(self, sentence: str) -> None:
        res = self.tagger.parse(sentence)
        tokens = res.splitlines()

        current_sentence_length = 0

        for token in tokens:
            if token == 'EOS':
                if current_sentence_length > 0:
                    self.sentence_lengths.append(current_sentence_length)
                current_sentence_length = 0
                break

            self.all_tokens_count += 1

            token_info = token.split(",")
            if token_info[0] == "":  # this happened for "Are you kidding me, kidding me?" sentence in Silent Cry
                continue
            try:
                value, part_of_speech = token_info[0].split("\t") # pos is relevant if VERB or AUXILIARY_VERB
            except ValueError:
                continue

            if len(value) == 1:
                if get_char_type(value) in SENTENCE_ENDING_CHARACTER_TYPES:
                    if current_sentence_length > 0:
                        self.sentence_lengths.append(current_sentence_length)
                    current_sentence_length = 0
                # should non-letters (eg. commas, quote open, dots) count toward sentence length?
                # currently only count letters
                elif get_char_type(value) in LETTER_TYPES:
                    current_sentence_length += 1
            else:
                current_sentence_length += len(value)
            
            # print(f"token: {value} pos: {part_of_speech} category: {word_category} additional info: {additional_info}")


            if part_of_speech == AUXILIARY_VERB_TAG:
                self.auxiliary_verbs_count += 1

            if part_of_speech == VERB_TAG:
                self.verb_count += 1

            try:
                word_category = token_info[12] # relevant if WAGO or KANGO
            except IndexError:
                continue

            if word_category == WAGO_TAG:
                self.wago_count += 1

            if word_category == KANGO_TAG:
                self.kango_count += 1

        print(
            f"all tokens: {self.all_tokens_count}, "
            f"verbs: {self.verb_count}, "
            f"auxiliary verbs: {self.auxiliary_verbs_count}, "
            f"wago: {self.wago_count}, "
            f"kango: {self.kango_count}, "
            f"sentence length: {current_sentence_length}"
            )

    # assumption: proportion means percentage (number of percent points) otherwise results don't make sense
    def calculate_readability_factors(self):
        self.readability_factors[
            MEAN_SENTENCE_LENGTH
            ] = sum(self.sentence_lengths) / len(self.sentence_lengths)
        self.readability_factors[KANGO_PROPORTION] = 100 * self.kango_count / self.all_tokens_count
        self.readability_factors[WAGO_PROPORTION] = 100 * self.wago_count / self.all_tokens_count
        self.readability_factors[VERB_PROPORTION] = 100 * self.verb_count / self.all_tokens_count
        self.readability_factors[AUXILIARY_VERB_PROPORTION] = 100 * self.auxiliary_verbs_count / self.all_tokens_count
        
        for name, value in self.readability_factors.items():
            print(f"factor: {name}, value: {value}")
        return self.readability_factors
    
    def calculate_readability_score(self) -> float:
        # sanity check
        assert(len(self.readability_factors)) == 6

        factors = [
            ReadabilityFactor(
                factor_name, WEIGHTS[factor_name], self.readability_factors[factor_name]
                ) for factor_name in self.readability_factors.keys()
        ]

        for factor in factors:
            print(f"name: {factor.name} value: {factor.value} weight: {factor.weight}")
        readability_score = 0.0
        for factor in factors:
            readability_score += factor.value * factor.weight
        return readability_score

# case from youkoso chikyuu san one of stories: "\"......, J'en ai déjà trois, Enfin voila! /Au revoir, tu verras ça.\""
# each token counts towards all tokens but sentence length is 0
# todo: calculate score and factors for each book and save somewhere
if __name__=="__main__":
    titles = {'bokko_chan', 'youkoso_chikyuu_san', 'kimagure_robotto', 'doujidai_geemu', 'silent_cry', 'torikaeko'}
    results = {}

    for title in titles:
        with open(f"texts/{title}.txt", "r") as text_file:
            text = text_file.read()

        leeform = LeeReadabilityFormula()
        leeform.parse_text(text)
        factors = leeform.calculate_readability_factors()
        score = leeform.calculate_readability_score()
        weighted_factors = {name: factors[name] * WEIGHTS[name] for name in factors}
        results[title] = {'score': score, 'factors': factors, 'weighted factors': weighted_factors}
    with open("leeform.pkl", "wb") as results_pickle_file:
        pickle.dump(results, results_pickle_file)
        # with open("results.txt", "a") as results_file:
        #     results_file.write(f"Title: {title}\n")
        #     results_file.write(f"Score: {score}\n")
        #     results_file.write(f"Factors: {factors}\n\n")
    # leeform = LeeReadabilityFormula()
    # leeform.parse_text("\"......, J'en ai déjà trois, Enfin voila! /Au revoir, tu verras ça.\"")