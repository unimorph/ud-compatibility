# ud-compatibility
Utility for converting Universal Dependencies–annotated corpora to UniMorph


The [Universal Dependencies (UD)](http://universaldependencies.org) and [Universal Morphology (UniMorph)](https://unimorph.github.io) projects each present schemata for annotating the morphosyntactic details of a language.
Each project also provides corpora of annotated text in many languages—UD at the token level and UniMorph at the type level.
As each corpus is built by different annotators, **language-specific decisions hinder the goal of universal schemata**.
**To ease this interoperability, we present a deterministic mapping** from Universal Dependencies&nbsp;v2 features into the UniMorph schema.


### Prerequisites

- termcolor: `pip install termcolor`
- Python 3.5 or later; Anaconda is a simple way to install it.

### Usage

The driver of the entire endeavor is the file `marry.py`, which marries a UD dataset to its affiliated UniMorph.

First, update the paths in `paths.py` to reflect where your UD (and UniMorph, if evaluating) data are stored.

#### Conversion

To convert *one* file to UniMorph, give the path (and optionally the specific language converter you'd like to use).

```bash
python marry.py convert --ud my/ud/path/rw-ud-dev.conllu
python marry.py convert --ud my/ud/path/da-ud-dev.conllu -l da

```

To convert your UD dataset to UniMorph, list the languages you'd like to convert:

```bash
python marry.py convert --langs he ro de it no_bokmaal 
```

When the input looks like this:

```
# sent_id = es-train-001-s21
# text = Tiene 2 madres.
1	Tiene	tener	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_
2	2	2	NUM	_	NumType=Card	3	nummod	_	_
3	madres	madre	NOUN	_	Gender=Masc|Number=Plur	1	obj	_	SpaceAfter=No
4	.	.	PUNCT	_	_	1	punct	_	_
```

The output will look like this:

```
# sent_id = es-train-001-s21
# text = Tiene 2 madres.
1	Tiene	tener	VERB	_	PRS;V;FIN;3;IND;SG	0	root	_	_
2	2	2	NUM	_	NUM	3	nummod	_	_
3	madres	madre	NOUN	_	N;PL;MASC	1	obj	_	SpaceAfter=No
4	.	.	PUNCT	_	_	1	punct	_	_
```

#### Evaluation

To assess a conversion (either of the included `Translator` objects or your own), the syntax is similar:

```bash
python marry.py evaluate --langs he ro de it no_bokmaal 
```

#### Replication

To replicate the experiments from the paper, use:

```bash
python marry.py replicate 
```

### Data

The individual datasets for Universal Dependencies v2 and UniMorph can be downloaded from their respective projects on GitHub.

## Contributing

You're welcome to submit a pull request, harmonizing your UD dataset with the corresponding UniMorph. 

1. Write your own `Translator` subclass.
2. Register it in the `languages.py` list.
3. Submit the Pull Request.

## License

This project is licensed under the GNU GPL v3 license; see the [LICENSE.md](LICENSE.md) file for details.

## Citation

```
@inproceedings{mccarthy2018udw,
	title = {Marrying Universal Dependencies and Universal Morphology},
	author = {Arya D. McCarthy and Miikka Silfverberg and Ryan Cotterell and Mans Hulden and David Yarowsky},
	booktitle = {Proceedings of the EMNLP 2018 Workshop on Universal Dependencies (UDW 2018)},
	address = {Brussels, Belgium}
	month = {October}
	year = {2018}
}
```
