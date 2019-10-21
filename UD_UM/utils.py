import csv
from collections import namedtuple
from pathlib import Path
from typing import Dict, Iterable, NewType
from collections.abc import Set

from paths import UD2UM_FILE


# UdTag = NewType("UdTag", str)
UmTag = NewType("UmTag", str)
UdFeat = NewType("UdFeat", str)
UmFeat = NewType("UmFeat", str)


class UdTag(Set):
    def __init__(self, tag: str) -> None:
        self.data = set(tag.split("|"))

    def __contains__(self, value):
        return value in self.data

    def __iter__(self):
        yield from self.data

    def __len__(self):
        return len(self.data)


def ud_iterator(file: Path) -> Iterable[str]:
    with open(file, encoding="utf-8") as f:
        yield from (line.strip() for line in f)


class CoNLLRow(
    namedtuple(
        "CoNLLRow", "id form lemma upostag xpostag " "feats head deprel deps misc"
    )
):
    @classmethod
    def make(cls, string: str) -> "CoNLLRow":
        return cls._make(string.split("\t"))


def is_conll_useless(line: str) -> bool:
    if line == "":
        return True
    if line.startswith("#"):
        return True
    return False


def _ud2um_mapping() -> Dict[UdFeat, UmFeat]:
    ud2um = {}
    with open(UD2UM_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            ud = UdFeat(row["UD"])
            um = UmFeat(row["UniMorph"] or "_")
            ud2um[ud] = um
    print(ud2um)
    return ud2um


ud2um_mapping = _ud2um_mapping()
