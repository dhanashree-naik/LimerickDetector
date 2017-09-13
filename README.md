# LimerickDetector

A limerick is defined as a poem with the form AABBA, where the A lines rhyme with each other, the B lines rhyme with each other, and the A lines do not rhyme with the B lines

## Implemeted Functions:
1. num syllables: count the number of syllables in a word
2. rhymes: detect whether two words rhyme or not
3. is limerick: given a candidate limerick, return whether it meets the constraint or not.
4. guess_syllables: reasonable guess for the number of syllables without using CMUdict
5. apostrophe tokenize: handles apostrophes in words correctly so that “can’t” would rhyme with “pant”

## What does it mean for two words to rhyme?
They should share the same sounds in their pronunciation except for their first consonant sound(s) and anything before their first consonant sounds. (This is a very strict definition of rhyming. This makes the assignment easier.) If one word is longer than the other, then the sounds of the shorter word (except for its first consonant sound and anything before the first consonant sound) should be a suffix of the sounds of the longer.

## Input :
Anything out of these:
1. stdin
2. textfile piped into the code. (eg: python limerick.py < input.txt)
