import re
from collections import Counter
import numpy as np


# How spelling correction works?
# 1: Selection mechanism > argmax
# 2: Candidate model using simple edit deletion, transposition, replacement, and insertion
# 3: Know word: Candidate model might generate a lot of candidates
# so we restrict to words that are known in the dictionary
# 4: Error model: edit distance  0>1>2
# priority of the candidates
# 1) The original word
# 2) the edit distance 1>
# 3) the edit distance 2>
# 4) the original word even though it is not know


# 0: readfile
def words(text): return re.findall(r'\w+', text.lower())


word_count = Counter(words(open('big 2.txt').read()))
N = sum(word_count.values())

letters = 'abcdefghijklmnopqrstuvwxyz'


def splits_word(word):
    return [(word[:i], word[i:]) for i in range(len(word) + 1)]


# remove redundancy e.g. pararameter -> parameter
def remove_redundancy(word):
    for L, R in splits_word(word):
        if len(L[-2:]) == 2 and len(R[:2]) == 2 and L[-2:] == R[:2]:
            word = L[:-2] + L[-2:] + R[2:]
            break
    return word


# switch uk 's' to us 'z'
def switch_uk_s_to_us_z(word):
    for L, R in splits_word(word):
        if len(L) > 0 and len(R) > 0 and L[-1] == 'i' and R[0] == 's':
            word = L + 'z' + R[1:]
            break
    return word


def remove_non_existing_duplicate(word):
    for L, R in splits_word(word):
        if len(L) > 0 and len(R) > 0 and L[-1] == R[0] and L[-1] in ('a', 'u'):
            word = L + R[1:]
            break
    return word


def switch_to_us_er_suffix(word):
    for L, R in splits_word(word):
        if len(L) > 0 and len(R) > 0 and L[-1] == 'r' and R[0] == 'e':
            word = (L[:-1] + R[0] + L[-1] + R[1:])
            break
    return word


def decorate(word):
    word = remove_redundancy(word)
    word = switch_uk_s_to_us_z(word)
    word = remove_non_existing_duplicate(word)
    # switch suffix uk '-re' to us '-er'
    word = switch_to_us_er_suffix(word)
    return word


def replace_suffixes(word):
    suffixes = {"aly": "ally",
                "cly": "cally",
                "led": "lled",
                "lys": "lies",
                "ice": "ise"}
    suffix = word[-3:]
    try:
        replaced = suffixes[suffix]
        word = word.replace(suffix, replaced)
        return [word]
    except:
        return []


# 1: choose a candidate by generating candidates with edit operation
# Try if we could add more edition
def candidates(word):
    return known([word]).union(replace_suffixes(word)) or known(
        edits1(word)) or known(edits2(word)) or [decorate(word)]


def edits1(word):
    splits = splits_word(word)
    deletes = [(L + R[1:]) for L, R in splits if R]

    insert_double_consonant = [(L + R[0] + R[0] + R[1:])
                               for L, R in splits
                               if len(L) > 0 and len(R) > 0 and
                               L[-1] in ('a', 'e', 'i', 'o', 'u')
                               and R[0] in ('d', 's', 'l')]

    double_p = [(L + R[0] + R[0] + R[1:]) for L, R in splits
                if len(L) > 0 and len(R) > 0 and
                L[-1] == 'a' and R[0] == 'p']

    double_o_e = [(L + R[0] + R[0] + R[1:]) for L, R in splits
                  if len(L) > 0 and len(R) > 0 and
                  R[0] in ('o', 'e')]

    transposes = [(L + R[1] + R[0] + R[2:]) for L, R in splits if len(R) > 1]
    replaces = [(L + c + R[1:]) for L, R in splits if R for c in letters]
    inserts = [(L + c + R) for L, R in splits for c in letters]

    return set(
        replaces + insert_double_consonant +
        double_o_e + double_p +
        deletes + transposes + inserts)


def edits2(word):
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


# 2: probability of each candidate from dictionary
def known(words):
    return set(w for w in words if w in word_count)


# 3: probability of generated candidates
def P(word): return word_count[word] / N  # float


# 4: choose candidate by argmax
def correction(word):
    return max(candidates(word), key=P)


# Unit-test
def unit_tests():
    # assert correction('parametres') == 'parameters'  # insert
    # assert correction('aalysing') == 'analysing'  # insert
    assert correction('speling') == 'spelling'  # insert
    assert correction('korrectud') == 'corrected'  # replace 2
    assert correction('bycycle') == 'bicycle'  # replace
    assert correction('inconvient') == 'inconvenient'  # insert 2
    assert correction('arrainged') == 'arranged'  # delete
    assert correction('peotry') == 'poetry'  # transpose
    assert correction('peotryy') == 'poetry'  # transpose + delete
    assert correction('word') == 'word'  # known
    assert correction('quintessential') == 'quintessential'  # unknown
    assert words('This is a TEST.') == ['this', 'is', 'a', 'test']
    assert Counter(words('This is a test. 123; A TEST this is.')) == (
        Counter({'123': 1, 'a': 2, 'is': 2, 'test': 2, 'this': 2}))
    assert len(word_count) == 32198
    assert sum(word_count.values()) == 1115585
    assert word_count.most_common(10) == [
        ('the', 79809),
        ('of', 40024),
        ('and', 38312),
        ('to', 28765),
        ('in', 22023),
        ('a', 21124),
        ('that', 12512),
        ('he', 12401),
        ('was', 11410),
        ('it', 10681)]
    assert word_count['the'] == 79809
    assert P('quintessential') == 0
    # assert 0.07 < P('the') < 0.08
    return 'unit_tests pass'


def spelltest(tests, verbose=False):
    "Run correction(wrong) on all (right, wrong) pairs; report results."
    import time
    start = time.process_time()
    good, unknown = 0, 0
    n = len(tests)
    for right, wrong in tests:
        w = correction(wrong)
        good += (w == right)
        if w != right:
            unknown += (right not in word_count)

            if verbose:
                print('correction({}) => {} ({}); expected {} ({})'
                      .format(wrong, w, word_count[w], right, word_count[right]))
    dt = time.process_time() - start
    print('{:.0%} of {} correct ({:.0%} unknown) at {:.0f} words per second '
          .format(good / n, n, unknown / n, n / dt))


def Testset(lines):
    "Parse 'right: wrong1 wrong2' lines into [('right', 'wrong1'), ('right', 'wrong2')] pairs."
    return [(right, wrong)
            for (right, wrongs) in (line.split(':') for line in lines)
            for wrong in wrongs.split()]
