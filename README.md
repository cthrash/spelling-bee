# Spelling Bee Library

I play the Spelling Bee puzzle on New York Times nearly every day (twice on Sunday!) and started to wonder about a few basic things:

- What is the greatest number of pangrams?
- What are least/most points?
- What is the longest possible word?
- What are the most/least common words?
- Are there puzzles for which genius cannot be achieved without the benefit of four-letter words?

The first thing I realized is that I don't have the same list of words used by the Times.  So I went on the make the best approximation.  My first thought was to start with the most commonly used words and whittle it down from that.  Based on this thought I landed [here](https://norvig.com/ngrams/).  The problem with web n-gram data is that it is very noisy.  For example, non-dictionary words like `wwww` have a surprisingly high count.  Another problem is that these corpora tend to be normalized (all lowercase, for example) in order to prevent n-gram counts from getting diluted.  This in turn poses a challenge when rooting out proper nouns.

So the next attempt was to use the dictionary that is installed on Ubuntu by default (with ispell?).  I'm running Ubuntu 20 if that matters.  The dictionary contains ~100K words.  I whittled this down to ~19K words by removing:

- proper nouns
- words with any punctuation
- words that include the letter 's'
- words that include accented characters
- words shorter than 4 letters long
- words containing more than 7 unique letters

## Answers

### The most pangrams

```python
>>> from spelling_bee.bee import Bee
>>> bee = Bee()
>>> scores = bee.score_tree()
>>> longest = max(scores, key=lambda score: score.pangrams)
>>> longest
Score(score=1654, key='a:eginrt', pangrams=22, words=235)
```

Naturally any permutation of the key would have the same number of pangrams:

```python
>>> for score in scores:
...   if score.pangrams==longest.pangrams:
...     print(score)
...
Score(score=1654, key='a:eginrt', pangrams=22, words=235)
Score(score=1739, key='e:aginrt', pangrams=22, words=251)
Score(score=1621, key='g:aeinrt', pangrams=22, words=218)
Score(score=1731, key='i:aegnrt', pangrams=22, words=232)
Score(score=1891, key='n:aegirt', pangrams=22, words=263)
Score(score=1809, key='r:aegint', pangrams=22, words=257)
Score(score=1605, key='t:aeginr', pangrams=22, words=228)
```

The list of pangrams are as follows:

```python
>>> bee.list_words('a:eginrt')[0]
['aerating', 'aggregating', 'entertaining', 'entreating', 'generating', 'granite', 'ingrate', 'ingratiate', 'integrate', 'integrating', 'iterating', 'regenerating', 'reiterating', 'retaining', 'retraining', 'retreating', 'tangerine', 'tangier', 'targeting', 'tattering', 'tearing', 'treating']
```

The number of pangrams per puzzle breaks down like this:

```python
>>> counts = defaultdict(int)
>>> for score in scores:
...   counts[score.pangrams] += 1
...
>>> for i in range(1,23):
...   print(f"{i:>2}: {counts.get(i,0)}")
...
 1: 19789
 2: 4452
 3: 1491
 4: 644
 5: 315
 6: 217
 7: 91
 8: 56
 9: 21
10: 21
11: 7
12: 0
13: 7
14: 0
15: 0
16: 7
17: 0
18: 0
19: 0
20: 0
21: 0
22: 7
```

Not surprisingly most puzzles have only a single pangram.  What's unexpected are the gaps between some puzzles with higher pangram counts.

### Least/most points

```python
>>> def f(minmax, scores):
...   top = minmax(scores, key=lambda v:v.score)
...   for score in scores:
...     if score.score == top.score:
...       print(score)
...
>>> f(max, scores)
Score(score=1891, key='n:aegirt', pangrams=22, words=263)
>>> f(min, scores)
Score(score=14, key='x:ahnpry', pangrams=1, words=1)
Score(score=14, key='x:bejkou', pangrams=1, words=1)
```

So there are two puzzles with a single pangram as the only answer:

```python
>>> for key in ['x:ahnpry', 'x:bejkou']:
...   print(bee.list_words(key))
...
(['pharynx'], [])
(['jukebox'], [])
```

According to a [site](https://www.sbsolver.com/stats) that tracks these sort of things, the lowest score published as of this writing is 47.  The highest is 537.

```python
>>> len([_ for score in scores if 47 <= score.score <= 517])
22658
>>> len(scores)
27125
>>> 22658/27125
0.8353179723502304
```

This means that the range of scores covers 83% of all possible puzzles.

To highlight the difference between my dictionary and the one used by the Times, you will see some variation in the keys that resulted in official highest/lowest overall score:

```python
>>> [score for score in scores if score.key=='i:cenotv']
[Score(score=459, key='i:cenotv', pangrams=6, words=64)]
>>> [score for score in scores if score.key=='f:imorty']
[Score(score=52, key='f:imorty', pangrams=1, words=17)]
```

The official dictionary had scores of `537/7/75`, `47/1/16`, respectively.

Incidentally, the puzzle with the most words is not the puzzle with the highest score.

```python
>>> max(scores, key=lambda v:v.words)
Score(score=1809, key='e:adinrt', pangrams=6, words=307)
```

### Longest word

The longest word in my dictionary has 15 letters, and there are four different ones.

```python
>>> most = len(max(bee.words_dict.keys(), key=lambda s:len(s)))
>>> most
15
>>> for word in bee.words_dict:
...   if len(word) == most:
...     print(word)
...
inconveniencing
interconnection
nationalization
nonintervention
```

It just so happens that we've gotten (at least) one of them playing the daily puzzle: `nationalization`. 

### Most/least common words

```python
>>> total_puzzles = len(scores)
>>> total_puzzles
27125
>>> total_words = sum([score.words for score in scores])
>>> total_words
1571249
```

With my dictionary, there are **27125** total possible puzzles.  

```python
>>> word_frequency = bee.count_words()
>>> unique_words = len(word_frequency)
>>> unique_words
18560
>>> total_words / unique_words
84.6578125
```

The average number of puzzles a given word appears in is about **85**.  The question then is which words appear in the most/fewest puzzles?  

```python
>>> sorted_word_frequency = sorted(word_frequency, key=lambda k:word_frequency[k])
>>> for i in range(5):
...   word = sorted_word_frequency[~i]
...   print(f"{word:>10}:{word_frequency[word]}")
...
    inning:2262
   ginning:2262
   gigging:2262
    deeded:2166
      deed:2166
>>> for i in range(5):
...   word = sorted_word_frequency[i]
...   print(f"{word:>10}:{word_frequency[word]}")
...
      fuzz:3
      flax:4
      jamb:4
     hubby:4
     jello:4
```
The word `inning` (and two other words that share the same letters) appear in **2262** puzzles. By contrast, `fuzz` appears in only **3**.  The three are for the pangram `futzing`, with the center letter being one of the three letters in `fuzz`.

```python
>>> fuz = {'f', 'u', 'z'}
>>> for score in scores:
...   key = score.key
...   if key[0] in fuz and all([letter in key for letter in fuz]):
...     print(score)
...
Score(score=94, key='f:gintuz', pangrams=1, words=19)
Score(score=115, key='u:fgintz', pangrams=1, words=21)
Score(score=45, key='z:fgintu', pangrams=1, words=9)
>>> bee.list_words('z:fgintu')
(['futzing'], ['fizz', 'fizzing', 'futz', 'fuzing', 'fuzz', 'fuzzing', 'zing', 'zinging'])
```

### Non GN4L-possible puzzles?

One of the ways we play the puzzle is to aim to achieve genius level (70% of total possible points) without the benefit of 4-letter words.  Among the aficionados, this feat is known by the initialism GN4L (Genius, No 4-Letters.)  By the daily Spelling Bee rules, 4-letter words are only worth one point.

Whenever we struggle with a puzzle, the thought crosses the mind -- is GN4L attainable with this puzzle?

```python
>>> for score in scores:
...   genius = int(score.score * 0.7)
...   p, np = bee.list_words(score.key)
...   n4l_score = sum([bee.words_dict[word].points for word in p + [w for w in np if len(w)>4]])
...   if n4l_score < genius:
...     print(score)
...
Score(score=26, key='w:abcikl', pangrams=1, words=11)
Score(score=33, key='e:abjnow', pangrams=1, words=14)
Score(score=74, key='l:abhitu', pangrams=2, words=30)
Score(score=38, key='u:abilot', pangrams=1, words=17)
Score(score=31, key='k:acegmo', pangrams=1, words=13)
Score(score=80, key='l:acgmou', pangrams=1, words=35)
Score(score=32, key='w:adfiln', pangrams=1, words=14)
Score(score=31, key='u:adfprt', pangrams=1, words=14)
Score(score=76, key='l:adiotu', pangrams=1, words=35)
Score(score=69, key='o:aelmpu', pangrams=1, words=29)
Score(score=30, key='f:agmnor', pangrams=1, words=13)
Score(score=31, key='d:bckoru', pangrams=1, words=14)
Score(score=34, key='b:cflotu', pangrams=1, words=16)
Score(score=71, key='l:bcfotu', pangrams=1, words=32)
Score(score=73, key='o:bcfltu', pangrams=1, words=32)
Score(score=69, key='l:bdfotu', pangrams=1, words=31)
Score(score=73, key='o:bdfltu', pangrams=1, words=35)
Score(score=53, key='t:bdflou', pangrams=1, words=23)
Score(score=48, key='l:bgnouw', pangrams=1, words=22)
Score(score=61, key='o:bglnuw', pangrams=1, words=26)
Score(score=22, key='u:bglnow', pangrams=1, words=9)
Score(score=64, key='l:bhinot', pangrams=1, words=26)
Score(score=39, key='l:bhnoru', pangrams=1, words=16)
Score(score=78, key='o:celmpx', pangrams=1, words=33)
Score(score=55, key='r:dfiotw', pangrams=1, words=23)
Score(score=43, key='d:gmopru', pangrams=1, words=18)
Score(score=59, key='l:dhiotw', pangrams=1, words=27)
Score(score=60, key='l:dhmotu', pangrams=1, words=24)
Score(score=59, key='l:dinotu', pangrams=1, words=27)
Score(score=39, key='f:ehlopu', pangrams=1, words=16)
Score(score=56, key='o:efklmn', pangrams=1, words=27)
Score(score=61, key='o:fhlmtu', pangrams=1, words=27)
Score(score=81, key='o:fiklrt', pangrams=1, words=35)
Score(score=38, key='i:klnrwy', pangrams=1, words=17)
```

So the answer is a resounding **yes**, there are puzzles for which GN4L is not possible.  Just as a sanity check I picked one of these somewhat randomly: `Score(score=74, key='l:abhitu', pangrams=2, words=30)`.  This one is interesting primarily because it is the only one with more than one pangram.

```python
>>> pangrams, nonpangrams = bee.list_words('l:abhitu')
>>> pangrams
['habitual', 'halibut']
>>> four_letter_words = [word for word in nonpangrams if len(word)==4]
>>> len(four_letter_words)
24
>>> four_letter_words
['alit', 'bail', 'ball', 'bill', 'blab', 'blah', 'bulb', 'bull', 'hail', 'hall', 'halt', 'haul', 'hill', 'hilt', 'hula', 'hull', 'lath', 'lilt', 'luau', 'lull', 'tail', 'tall', 'till', 'tilt']
```

Out of the total **74** points, **24** are from four-letter words, but you need **51** points for genius.

## Using this library

If you want to use my dictionary, simply create a `Bee` object and use as shown above.  You can also instantiate a `Bee` object from a list of words or from a file containing a list of words.

You can create your own filtered dictionary from the command line.  The filter expects one word per line.

```bash
poetry run filter < in_file > out_file
```

You can instantiate a `Bee` object with your file:

```python
bee = Bee.from_file(path_to_out_file)
```

## Requirements
- Python 3.9+
- poetry

