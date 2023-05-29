import pickle

import tateisi_formula
import lee_formula

if __name__=="__main__":
    titles = {'bokko_chan', 'youkoso_chikyuu_san', 'kimagure_robotto', 'doujidai_geemu', 'silent_cry', 'torikaeko'}
    results = {'tatform': {}, 'leeform': {}}

    for title in titles:
        print(f"calculating readability metrics for {title}")
        with open(f"texts/{title}.txt", "r") as text_file:
            text = text_file.read()
        tatform = tateisi_formula.TateisiReadabilityFormula(text)
        score = tatform.calculate_readability_score()
        factors = tatform.readability_factors
        weighted_factors = {name: factors[name] * tateisi_formula.WEIGHTS[name] for name in factors}
        results['tatform'][title] = {'score': score, 'factors': factors, 'weighted factors': weighted_factors}

        leeform = lee_formula.LeeReadabilityFormula(tatform.sentence_lengths, text)
        factors = leeform.calculate_readability_factors()
        score = leeform.calculate_readability_score()
        weighted_factors = {name: factors[name] * lee_formula.WEIGHTS[name] for name in factors}
        results['leeform'][title] = {'score': score, 'factors': factors, 'weighted factors': weighted_factors}
    with open("tatform.pkl", "wb") as results_pickle_file:
        pickle.dump(results['tatform'], results_pickle_file)
    with open("leeform.pkl", "wb") as results_pickle_file:
        pickle.dump(results['leeform'], results_pickle_file)