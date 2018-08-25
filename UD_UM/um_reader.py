from collections import defaultdict
from pathlib import Path
from typing import Iterable, Tuple, Set, Dict


def _read_unimorph(fname: Path) -> Iterable[Tuple[str, str, Set[str]]]:
    with open(fname, encoding='utf-8') as f:
        for line in f:
            if line.split():
                try:
                    lemma, inflected, features = line.strip().split("\t")
                except ValueError:
                    print("Line:", line.split())
                    raise
                yield (inflected, lemma, set(features.split(";")))


def _as_dict_of_sets(rows: Iterable[Tuple[str, str, Set[str]]]) -> Tuple[dict, dict]:
    tags = defaultdict(set)
    lemmas = defaultdict(set)
    for form, lemma, tag in rows:
        tags[form].add(frozenset(tag))
        lemmas[form].add(lemma)
    return dict(tags), dict(lemmas)

def unimorph(fname: Path) -> Tuple[dict, dict]:
    return _as_dict_of_sets(_read_unimorph(fname))