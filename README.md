# MENSABLE (TODO: add hosted web app url here)

#### Video Demo: (TODO: add video url here)

## Introduction

Mensable - from the Latin *mens, mentis: mind, plan, intention* - is a web app
for learning lists (in mensable, 'tables') of foreign language vocabulary, IT
acronym definitions, historical dates or any other information that can be put
on a flashcard. 

Tables are organized into 'languages' and contain 'word pairs'. Users can
browse, subscribe to and take quizzes on existing word tables as well as
creating their own.

When a user takes quizzes on a table, mensable uses the [Leitner
system](https://en.wikipedia.org/wiki/Leitner_system) to keep track of the
user's progress. This is a simple 'spaced-repetition' algorithm for
flashcard-based learning software where word pairs are sorted into an array of
'boxes' for each user. All word pairs start in the 'lowest' box (box 0) and are
moved along to a higher box when answered correctly in a quiz. Quizzes always
cover the words in the lowest-ranked boxes, and an incorrect answer for a word
pair demotes it back to box 0. This system ensures that the maximum time is
spent on the hardest word pairs.

