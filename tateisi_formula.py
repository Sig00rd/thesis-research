from typing import Dict, List
from character_type import get_char_type, CharType

ALPHABET_RUNS_PERCENTAGE = "ALPHABET_RUNS_PERCENTAGE"
HIRAGANA_RUNS_PERCENTAGE = "HIRAGANA_RUNS_PERCENTAGE"
KANJI_RUNS_PERCENTAGE = "KANJI_RUNS_PERCENTAGE"
KATAKANA_RUNS_PERCENTAGE = "KATAKANA_RUNS_PERCENTAGE"
LETTERS_PER_ALPHABET_RUN = "LETTERS_PER_ALPHABET_RUN"
LETTERS_PER_HIRAGANA_RUN = "LETTERS_PER_HIRAGANA_RUN"
LETTERS_PER_KANJI_RUN = "LETTERS_PER_KANJI_RUN"
LETTERS_PER_KATAKANA_RUN = "LETTERS_PER_KATAKANA_RUN"
LETTERS_PER_SENTENCE = "LETTERS_PER_SENTENCE"
TOOTEN_TO_KUTEN_RATIO = "TOOTEN_TO_KUTEN_RATIO"
CONSTANT = "CONSTANT"

WEIGHTS = {
    ALPHABET_RUNS_PERCENTAGE: 0.06,  # number of runs/total run count
    HIRAGANA_RUNS_PERCENTAGE: 0.25,
    KANJI_RUNS_PERCENTAGE: -0.19,
    KATAKANA_RUNS_PERCENTAGE: -0.61,
    LETTERS_PER_SENTENCE: -1.34,  # count these 4 writing systems letters count per sentence
    LETTERS_PER_ALPHABET_RUN: -1.35,  # (I don't think digits and other symbols are letters)
    LETTERS_PER_HIRAGANA_RUN: 7.52,
    LETTERS_PER_KANJI_RUN: -22.1,
    LETTERS_PER_KATAKANA_RUN: -5.3,
    TOOTEN_TO_KUTEN_RATIO: -3.87,
    CONSTANT: -109.1
}

SENTENCE_ENDING_CHARACTER_TYPES = {
    CharType.KUTEN, CharType.END_QUOTE, CharType.EXCLAMATION_MARK, CharType.QUESTION_MARK
}

LETTER_TYPES = {
    CharType.ALPHABET, CharType.HIRAGANA, CharType.KANJI, CharType.KATAKANA
}

class ReadabilityFactor:
    def __init__(self, name: str, value: float, weight: float):
        self.name = name
        self.value = value
        self.weight = weight

class TateisiReadabilityFormula:
    def __init__(self, text: str) -> None:
        self.text = text
        self.tooten_count = 0
        self.kuten_count = 0
        self.sentence_lengths: List[int] = []
        self.runs: Dict[CharType, List[str]] = {
            char_type: [] for char_type in LETTER_TYPES
        }
        self.readability_factors: Dict[str, float] = {
            CONSTANT: 1.0
        }
        
        self.parse()
        self.tooten_kuten_ratio()
        self.runs_percentages()
        self.letters_per_runs()
        self.letters_per_sentence()

    def parse(self) -> None:
        current_run = ""
        current_run_type = None
        current_sentence_length = 0

        for character in self.text:
            current_char_type = get_char_type(character)
            if current_char_type == current_run_type:
                current_run += character
            else:
                if current_run_type in LETTER_TYPES:
                    self.runs[current_run_type].append(current_run)
                current_run = ""
                current_run_type = current_char_type
                current_run += character
            # only count letters for purpose of determining sentence length
            if current_char_type in LETTER_TYPES:
                current_sentence_length += 1
            if current_char_type == CharType.KUTEN:
                self.kuten_count += 1
            if current_char_type in SENTENCE_ENDING_CHARACTER_TYPES:
                # same principle, this time don't count non-letter "sentences" as sentences
                if current_sentence_length > 0:
                    self.sentence_lengths.append(current_sentence_length)
                    current_sentence_length = 0
            if current_char_type == CharType.TOOTEN:
                self.tooten_count += 1
    
    # todo: doublecheck rates /w paper
    def tooten_kuten_ratio(self) -> None:
        if self.kuten_count > 0:
            ratio = self.tooten_count / self.kuten_count
        else:
            ratio = 0
        self.readability_factors[TOOTEN_TO_KUTEN_RATIO] = ratio

    def runs_percentages(self) -> None:
        all_run_count = sum([len(self.runs[letter_type]) for letter_type in LETTER_TYPES])
        self.readability_factors[KANJI_RUNS_PERCENTAGE] = 100.0 * len(self.runs[CharType.KANJI]) / all_run_count
        self.readability_factors[KATAKANA_RUNS_PERCENTAGE] = 100.0 * len(self.runs[CharType.KATAKANA]) / all_run_count
        self.readability_factors[HIRAGANA_RUNS_PERCENTAGE] = 100.0 * len(self.runs[CharType.HIRAGANA]) / all_run_count
        self.readability_factors[ALPHABET_RUNS_PERCENTAGE] = 100.0 * len(self.runs[CharType.ALPHABET]) / all_run_count

    def letters_per_runs(self) -> None:
        def average_run_length(runs: List[str]) -> float:
            if not len(runs):
                return 0.0
            return sum([len(run) for run in runs]) / len(runs)

        readability_factors_keys_with_letter_types = [
            (LETTERS_PER_KANJI_RUN, CharType.KANJI),
            (LETTERS_PER_KATAKANA_RUN, CharType.KATAKANA),
            (LETTERS_PER_HIRAGANA_RUN, CharType.HIRAGANA),
            (LETTERS_PER_ALPHABET_RUN, CharType.ALPHABET)
        ]

        for result_key, letter_type in readability_factors_keys_with_letter_types:
            self.readability_factors[result_key] = average_run_length(self.runs[letter_type])
    
    def letters_per_sentence(self) -> None:
        if not len(self.sentence_lengths):
            return 0.0
        self.readability_factors[LETTERS_PER_SENTENCE] = sum(
            length for length in self.sentence_lengths
            ) / len(self.sentence_lengths)
                
    
    def calculate_readability_score(self) -> float:
        # sanity check
        assert(len(self.readability_factors)) == 11

        factors = [
            ReadabilityFactor(
                factor_name, self.readability_factors[factor_name], WEIGHTS[factor_name]
                ) for factor_name in self.readability_factors.keys()
        ]
        for factor in factors:
            print(f"name: {factor.name} value: {factor.value} weight: {factor.weight}")
        readability_score = 0.0
        for factor in factors:
            readability_score += factor.value * factor.weight
        print(readability_score)



if __name__ == "__main__":
    # text = "ゴジラはモスラと一所懸命に打ち合った。"
    with open("test_text.txt", "r") as text_file:
        text = text_file.read()
    tatform = TateisiReadabilityFormula(text)
    tatform.calculate_readability_score()
    # print(tatform.runs, tatform.sentence_lengths)