from collections import defaultdict
from pathlib import Path
from typing import Iterable, Tuple, Set, Dict


from .utils import Form, Lemma, UmFeat, UmFeats, UniMorphTriple


def _read_unimorph(fname: Path) -> Iterable[UniMorphTriple]:
    with open(fname, encoding="utf-8") as f:
        for line in f:
            if line.split():
                try:
                    lemma, inflected, features = line.strip().split("\t")
                except ValueError:
                    print("Line:", line.split())
                    raise
                features_typed = map(UmFeat, features.split(";"))
                yield UniMorphTriple(Form(inflected), Lemma(lemma), set(features_typed))


def _as_dict_of_sets(
    rows: Iterable[UniMorphTriple]
) -> Tuple[Dict[Form, Set[UmFeats]], Dict[Form, Set[Lemma]]]:
    tags: Dict[Form, Set[UmFeats]] = defaultdict(set)
    lemmas: Dict[Form, Set[Lemma]] = defaultdict(set)
    for form, lemma, tag in rows:
        tags[form].add(frozenset(tag))
        lemmas[form].add(lemma)
    return dict(tags), dict(lemmas)


def unimorph(fname: Path) -> Tuple[Dict[Form, Set[UmFeats]], Dict[Form, Set[Lemma]]]:
    return _as_dict_of_sets(_read_unimorph(fname))
