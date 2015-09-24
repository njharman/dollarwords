#!/usr/bin/env python
'''Dollar Words

An implementation by Norman Harman njharman@gmail.com 2015-09-24


Problem Statement:

Give each letter in each word a numerical value equal to its position in the
alphabet.  So "a" is 1 and "z" is 26.  Punctuation and whitespace is 0.  Find
words where the sum of the value of the letters is 100.  Print the list of words
ordered from shortest to longest.


Unstated Assumptions:
  - Entire word list it fits into memory.
  - Duplicate input words should be duplicated in output.
  - Ordering of words with same length does not matter and need not be stable.
  - No control chars (other than tab, newline, linefeed), no Unicode, no codepages (umlauts, etc.).
  - Word list contains no upper case letters.  Would be easy to adapt for
    uppercase letters with "word = word.lower()".


Implementation:

Considered two methods of getting dollar words in order.
  1. Pre-sort word list. Output dollar words as they are found.
  2. Accumulate dollar words in temporary list. Sort this dollar word list, then output.

  Seemed sensible to sort the smaller list.  Given that the input word list is
  likely to be much larger than dollar words.

  It might be faster to have "manually sorted" the dollar words as I found them.
  Say by stuffing into a dictionary keyed on len(word). Which would save the
  sort step. But, python's Timsort is pretty darn good. Would have to do real
  profiling to determine if it's worth it.

Considered three methods to calculate value of letter.

  1. ord(letter) minus fixed value (ord(a)).
     Ord is fastest but has major downside of being incorrect when whitespace
     and punctuation are considered. This could be overcome guarding for
     non-letters. But unless speed was requirement it's too "clever" and
     inflexible.

  2. Using index() into list of a-z.
     Since input's only punctuation is apostrophe whose value is 0 was able to
     exploit 0 based indexing by using list "'abc...". But that is rather
     inflexible and really doesn't meet problem statement (doesn't handle
     embedded whitespace or other punctuation). It is also slowest by ~2x. Which
     makes sense. Although short, it is still an O(n) linear lookup.

  3. Dictionary, letters -> values.
     Ended up using this method. First it is correct and fully meets problem
     statement. Not embarrassingly slow and barring performance requirement is
     fast enough, O(1). It is flexible; easy to adjust values of characters
     and extend with non-ASCII.  Finally, dictionary lookups are a very common
     Python idiom. I believe this method to be the clearest and simplest.

Instead of "for letter in word" loop could have done following. Which maybe is
marginally faster and/or preferred in functional oriented shops. Too me it is
a little "too much". Esp for a interview test which should lean towards
simplicity and flexibility.

>>> if sum(letter_values.get(l, 0) for l in word) == 100
>>>     dollar_words.append(word)


Typically I'd make "stream" processing functions like get_dollar_words()
generators. So they use constant memory and can be used with infinite streams.
Didn't fit use case here.


Simple Timing tests:

>>> from timeit import timeit
>>> print timeit('[v.index(l) for l in letters]', 'import string;v = "\'" + string.lowercase;letters="".join(l.strip() for l in open("american-words.80").readlines())', number=1000)
>>> 8.37283110619
>>> print timeit('[v.get(l,0) for l in letters]', 'import string;v = dict(zip(string.lowercase, range(1,27)));letters="".join(l.strip() for l in open("american-words.80").readlines())', number=1000)
>>> 4.79521799088
>>> print timeit('[ord(l) - 96 for l in letters]', 'letters="".join(l.strip() for l in open("american-words.80").readlines())', number=1000)
>>> 2.97817015648


Testing:
    run nosetests dollarwords.py

Would normally use separate file and unittest library. Splitting up test into
several methods. Would break out word value calculation into separate function
to test it independently. Didn't here for simplicity and python function call
overhead (which is poor reason). Probably spend some time making better test
values. Also, ~3s for (2) unittests is too slow. Would move the big'uns into
"integration" or some other test suite.


Other thoughts:

Normally I'd use stdlib argparse rather than hard code words filename .

A couple of commented out code lines I left in for purposes of elucidating my
thought process. Would delete before check in.

I really want to verify with "customer" about stripping left/right white space.
Actually, it bothered me too much. Ended up moving it outside. Just cleaner and
closer to one responsibility per function. See commented out line below.

TIL what zoogleas are.
'''
import string


def get_dollar_words(words):
    '''Given a=1,...,z=26, get words whose letters sum to 100.

    :param words: finite iterable of words consisting of lowercase letters, whitespace, and punctuation characters.
    :return: list of words whose letters add up to 100.
    '''
    # Keys to values: a-z -> 1-26.
    letter_values = dict(zip(string.lowercase, range(1, 27)))
    dollar_words = list()
    for word in words:
        # word = word.strip()  # Perhaps stripping whitespace is incorrect and should be moved outside?
        value = 0
        for letter in word:
            value += letter_values.get(letter, 0)
            if value > 100:  # Never gonna be a dollar, might as well give up.
                break
        if value == 100:
            dollar_words.append(word)
    return dollar_words


def sort_by_length(items):
    '''Items sorted by length of word.

    :param items: list of items that support len() protocol.
    :return: list, items sorted by length.
    '''
    items.sort(key=lambda w: len(w))
    return items


def test_get_dollar_words():
    from itertools import chain
    change = ['', '  ', 'some', 'words', 'that', 'do', 'not', 'add', 'up', 'to', 'a', 'dollar']
    # y=25, a+x=25
    dollar = ['yyyy', 'yyyy', 'yyyax', 'yyy !y', 'b' * 50, 'a' * 100]
    # Edge cases.
    assert list() == get_dollar_words([])
    assert list() == get_dollar_words(())
    # Dollars?
    assert list() == get_dollar_words(change)
    assert dollar == get_dollar_words(dollar)
    assert dollar == get_dollar_words(dollar + change)
    assert dollar == get_dollar_words(chain.from_iterable(zip(dollar, change, change)))
    assert dollar + dollar == get_dollar_words(dollar + change + dollar)
    # Big(ish) list of words.
    assert list() == get_dollar_words(change * 100000)
    assert dollar * 100000 == get_dollar_words(dollar * 100000)
    # Really big word.
    assert list() == get_dollar_words('money' * 10000)


def test_sort_by_length():
    from itertools import chain
    # In order shortest to longest.
    sorted = ['', (1, 2, 3), 'yyyy', 'yyyy', 'yyyax', 'b' * 50, 'a' * 100]  # y=25, a+x=25
    # Not in order.
    turned = list(reversed(sorted))
    # Keep the order, double the length.
    double = list(chain.from_iterable(zip(sorted, sorted)))
    # Edge cases.
    assert list() == sort_by_length([])
    # assert list() == sort_by_length(())  # Hmmm, tuples don't have sort. Ah, immutable.
    # Does it sort?
    assert sorted == sort_by_length(sorted)
    assert sorted == sort_by_length(turned)
    assert double == sort_by_length(sorted + sorted)
    assert double == sort_by_length(sorted + turned)


if __name__ == '__main__':
    words = [w.strip() for w in open('american-words.80').readlines()]
    dollar_words = get_dollar_words(words)
    sorted_words = sort_by_length(dollar_words)
    print '\n'.join(sorted_words)
