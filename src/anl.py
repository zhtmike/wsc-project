import collections
import functools
import itertools

import nlp
import schema


def is_root(item):
    return True if item['dep'] == 'ROOT' else False


def is_nsubj(item):
    return True if item['dep'] == 'nsubj' else False


def is_dobj(item):
    return True if item['dep'] == 'dobj' else False


def is_neg(item):
    return True if item['dep'] == 'neg' else False


def is_pronoun(tag):
    return True if tag in {'PRP'} else False


def is_adj(tag):
    return True if tag in {'JJ', 'JJR', 'JJS'} else False


def is_verb(tag):
    return True if tag in {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'} else False


def is_conjunction(tag):
    return True if tag in {'CC', 'IN', ',', ';'} else False


def is_neg_conjuction(conj):
    return True if conj in {'although', 'but'} else False


class SentenceParser():
    def __init__(self):
        self.parser = nlp.ContentParser()
        self.nlp = nlp.NLPFactory()
        self.chain = schema.read_schemas()
        self.verb_chain = schema.read_verb(self.chain)

    def anal(self, raw, pronoun, ans0, ans1):
        # try heuristics polarity first
        ans = self.heuristic_polarity(raw, pronoun, ans0, ans1)

        # if ans cannot be found, try narrative chain
        if not ans:
            ans = self.narrative_chain(raw, pronoun, ans0, ans1)
        return ans

    def heuristic_polarity(self, raw, pronoun, ans0, ans1):
        dep = self.parser.dependencies(raw)
        tag = self.parser.create_tagging(raw)
        lm = self.parser.create_lemma(raw)

        # skip non-descriptive sentence
        if not any([is_adj(v) for v in tag.values()]):
            return

        # get the adj describe the pronoun
        pron = self._get_dependency(dep, tag, pronoun)
        if not pron:
            return

        # get the dependencies of two antecedents
        ante = self._get_antecedents_dependency(dep, tag, ans0, ans1)

        # get the polarity of antecedents
        if ante and pron:
            sent_ante = self.parser.sentiment(
                self.nlp.annotate(lm[ante['gvn']]))
            sent_pronoun = self.parser.sentiment(
                self.nlp.annotate(lm[pron['adj']]))

            # serach if negation exists
            negs = list(filter(is_neg, dep.values()))
            if negs:
                for neg in negs:
                    if neg['gvn'] == ante['gvn']:
                        sent_ante = 4 - sent_ante
                    elif neg['gvn'] == pron['adj']:
                        sent_pronoun = 4 - sent_pronoun

            # search if negation conjuncgion exists
            conjs = list(filter(lambda x: is_conjunction(tag[x]), tag.keys()))
            neg_conj = list(filter(is_neg_conjuction, conjs))
            if neg_conj:
                sent_pronoun = 4 - sent_pronoun

            if sent_ante == 2 and sent_pronoun == 2:
                return ante['dobj']
            elif (sent_ante > 2 and sent_pronoun > 2) or (sent_ante < 2 and sent_pronoun < 2):
                return ante['dobj']
            else:
                return ante['nsubj']

    def _get_dependency(self, dep, tag, pronoun):
        # first trial
        if is_adj(tag[dep[pronoun]['gvn']]):
            return {'dep': dep[pronoun]['dep'], 'adj': dep[pronoun]['gvn']}

        # second trial
        adj = None
        for key in dep.keys():
            if is_adj(tag[key]):
                adj = key
                break
        if dep[adj]['gvn'] == dep[pronoun]['gvn']:
            return {'dep': dep[pronoun]['dep'], 'adj': adj}

        return {}

    def _get_antecedents_dependency(self, dep, tag, noun0, noun1):
        ante0 = noun0.split()[-1]
        ante1 = noun1.split()[-1]
        raw = {ante0: noun0, ante1: noun1}

        # two names should be nsubj and dobj separately
        if ante0 not in dep or ante1 not in dep:
            return {}

        # first trial
        if (dep[ante0]['dep'], dep[ante1]['dep']) in {('dobj', 'nsubj'), ('nsubj', 'dobj')}:
            rel = dict(
                zip((dep[ante0]['dep'], dep[ante1]['dep']), (ante0, ante1)))
            gvn = dep[rel['dobj']]['gvn']
            if is_adj(tag[gvn]) or is_verb(tag[gvn]):
                rel['gvn'] = gvn
                rel['dobj'] = raw[rel['dobj']]
                rel['nsubj'] = raw[rel['nsubj']]
                return rel

        # second trial
        if (dep[ante0]['dep'], dep[ante1]['dep']) in {('dobj', 'nmod'), ('nmod', 'dobj'), ('nmod', 'nsubj'), ('nsubj', 'nmod')}:
            rel = dict(
                zip((dep[ante0]['dep'], dep[ante1]['dep']), (ante0, ante1)))
            gvn = dep[rel['nmod']]['gvn']
            if is_adj(tag[gvn]) or is_verb(tag[gvn]):
                # nmod is robusted
                rel['gvn'] = gvn
                rel['dobj'] = raw[rel.get('dobj', rel['nmod'])]
                rel['nsubj'] = raw[rel.get('nsubj', rel['nmod'])]
                return rel

        return {}

    def narrative_chain(self, raw, pronoun, ans0, ans1):
        dep = self.parser.dependencies(raw)
        tag = self.parser.create_tagging(raw)
        lm = self.parser.create_lemma(raw)

        if sum([is_verb(v) for v in tag.values()]) < 2:
            return

        # extracted all verbs
        verbs = list(filter(lambda x: is_verb(tag[x]), tag.keys()))
        pairs = itertools.combinations(map(lambda x: lm[x], verbs), 2)
        pchains = list(filter(self._is_in_chain, pairs))

        if not pchains:
            return

        pron = self._get_dependency_verb(dep, tag, lm, pronoun)
        if not pron:
            return

        ante = self._get_antecedents_dependency(dep, tag, ans0, ans1)

        # find the verbs in narrative chain, with -s, -o correctly matched.
        if ante and pron:
            pair = {lm[ante['gvn']], lm[pron['verb']]}
            if self._is_in_chain(pair):
                pron['chain'] = lm[pron['verb']] + \
                    '-s' if pron['dep'] == 'nsubj' else lm[pron['verb']] + '-o'
                ante[ans0] = lm[ante['gvn']] + \
                    '-s' if ante['nsubj'] == ans0 else lm[ante['gvn']] + '-o'
                ante[ans1] = lm[ante['gvn']] + \
                    '-s' if ante['nsubj'] == ans1 else lm[ante['gvn']] + '-o'
                if self._is_in_narrative_chain({pron['chain'], ante[ans0]}):
                    return ans0
                elif self._is_in_narrative_chain({pron['chain'], ante[ans1]}):
                    return ans1

    def _is_in_chain(self, pair):
        pair = set(pair)
        for chain in self.verb_chain:
            if pair.issubset(chain):
                return True
        return False

    def _is_in_narrative_chain(self, pair):
        pair = set(pair)
        for chain in self.chain:
            if pair.issubset(chain):
                return True
        return False

    def _get_dependency_verb(self, dep, tag, lm, pronoun):
        # first trial
        if is_verb(tag[dep[pronoun]['gvn']]):
            return {'dep': dep[pronoun]['dep'], 'verb': dep[pronoun]['gvn']}

        return {}
