# French language tools
Series of tools using a French dictionary in .csv format.
The file contains +900,000 words with their spelling variations, their plurals, their conjugations etc. as well as their definitions, also in French. It was generated in Python on the basis of an XML file containing the database of fr.wiktionary and according to methods explained in detail in the "Upstream" folder, the XML not being in the final git due to its significant weight.

The .csv dataset was also published on Kaggle : https://www.kaggle.com/datasets/kartmaan/dictionnaire-francais

## French dictionary
Allows you to browse the dictionary, search for a word and retrieve its definition(s)

## Lexicon
Tools for saving dictionary or custom words to an Excel .xlsx file. The tool allows, among other things, to:
- Add words to the lexicon
- Find if a word is present in the lexicon
- Delete a word from the lexicon

## Word analyzer
Tools for multi-filtering words according to specific conditions:
- N-letter words
- Words starting with
- Words ending with
- Words that must contain such letters
- Words that must not contain such letters
- Words that must contain such letters at such rank
