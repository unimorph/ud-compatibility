import re
from collections import defaultdict
from typing import List, Set

from languages import languages
from utils import CoNLLRow, UdFeat, UdTag, UmFeat, UmTag, ud2um_mapping

EMPTY_FEAT = UmFeat("_")


def handle_arguments(ud: UdTag) -> List[UmFeat]:
    def handle_argument(parts):
        parts = str(parts)
        if "[psed]" in parts or "[gram]" in parts:
            return "_"

        if "[erg]" in parts:
            kind = "ER"
        elif "[dat]" in parts:
            kind = "DA"
        elif "[abs]" in parts:
            kind = "AB"
        else:
            print(parts)
            raise AssertionError

        if "=Plur" in parts:
            number = "P"
        elif "=Sing" in parts:
            number = "S"
        elif "=Dual" in parts:
            number = "D"
        else:
            assert "Number" not in str(parts)
            number = ""

        if "=1" in parts:
            person = "1"
        elif "=2" in parts:
            person = "2"
        elif "=3" in parts:
            person = "3"
        else:
            assert "Person" not in str(parts)
            person = ""
        return f"ARG{kind}{person}{number}"
    arg_parts = [p for p in ud if "[" in p and "[psor]" not in p]
    if not arg_parts:
        return [EMPTY_FEAT]
    arg_re = re.compile(r'\[(.*?)\]')
    tags = {arg_re.search(p).group(1) for p in arg_parts}
    contributions = []
    for tag in tags:
        arg = handle_argument([p for p in arg_parts if tag in p])
        if arg:
            contributions.append(arg)
    return contributions


def handle_possession(ud_tag: UdTag) -> UmFeat:
    psor_parts = [p for p in ud_tag if "[psor]" in p]
    if not psor_parts:
        return EMPTY_FEAT

    if "None" in str(psor_parts):
        return "PSSD"

    try:
        assert len(psor_parts) <= 2
    except AssertionError:
        print(psor_parts)
        raise

    if "Number[psor]=Plur" in psor_parts:
        number = "P"
    elif "Number[psor]=Sing" in psor_parts:
        number = "S"
    elif "Number[psor]=Dual" in psor_parts:
        number = "D"
    else:
        assert "Number" not in str(psor_parts)
        number = ""

    if "Person[psor]=1" in psor_parts:
        person = "1"
    elif "Person[psor]=2" in psor_parts:
        person = "2"
    elif "Person[psor]=3" in psor_parts:
        person = "3"
    else:
        assert "Person" not in str(psor_parts)
        person = ""

    return UmFeat(f"PSS{person}{number}")


def process_tag(part):
    try:
        um_part = ud2um_mapping[part]
    except KeyError:
        # print("Couldn't find", part)
        return "_"
    #     if part != "_":
            # if part in UD_valid_tags:
            #     self.no_match_tags.add(part)
            # else:
            #     self.invalid_tags.add(part)
    else:
        return um_part


def ud2um(ud_tag: UdTag) -> UmTag:
    um_tag: List[UmFeat] = []
    possession = handle_possession(ud_tag)
    um_tag.append(possession)
    arguments = handle_arguments(ud_tag)
    um_tag.extend(arguments)

    for part in ud_tag:
        if ',' not in part:
            tag = process_tag(part)
            um_tag.append(tag)
        else:
            key, vals = part.split("=")
            vals = vals.split(",")
            all_parts = []
            for val in vals:
                tag = process_tag(f"{key}={val}")
                all_parts.append(tag)
            all_parts = [p for p in all_parts if p != '_']
            um_tag.append(f"{{{'/'.join(all_parts)}}}" if all_parts else "_")
    um_tag = [f for f in um_tag if str(f) != "_"] or [EMPTY_FEAT]
    # print(um_tag)
    return UmTag(";".join(um_tag))


class Translator():
    def __init__(self, clever, replace_feats):
        self.clever = clever
        self.replace_feats = replace_feats

    def translate(self, record: CoNLLRow) -> CoNLLRow:
        ud_tag: UdTag = UdTag(f"{record.upostag}|{record.feats}")
        # print(ud_tag)
        um_tag: UmTag = self.basic_convert(ud_tag)

        if self.clever:
            um_tag = self.lgspec_modify(record, um_tag)

        if self.replace_feats:
            updated = record._replace(feats=um_tag)
        else:
            updated = record._replace(misc=um_tag)
        return updated

    def basic_convert(self, ud_tag: UdTag) -> UmTag:
        return ud2um(ud_tag)

    def lgspec_assert(self, cols: CoNLLRow, tags: Set[str]) -> None:
        """Override me."""
        pass

    def lgspec_modify(self, cols: CoNLLRow, um: UmTag) -> UmTag:
        return um


class BasqueTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        assert "V" in tags or "V.PTCP" in tags or "V.CVB" in tags or "V.MSDR" in tags


class BulgarianTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        assert "N" not in tags

    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        if "V" in tags:
            tags.discard("FIN")
            tags.discard("ACT")
            tags.discard("IPFV")
            tags.discard("PFV")
        if "V.PTCP" in tags:
            tags.discard("ADJ")
            tags.discard("V")
            if "PRS" in tags:
                tags.discard("IPFV")
            if "PASS" not in tags:
                tags.add("ACT")
            if "PFV" in tags:
                tags.discard("PFV")
                tags.add("PST")
        if "RL" in tags:
            tags.remove("RL")
            tags.add("SPRL")
        return ";".join(tags)


class CatalanTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        assert "V" in tags or "V.PTCP" in tags or "V.CVB" in tags or "V.MSDR" in tags

    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        # if "N" in tags:
        #     for gender in {"MASC", "FEM", "NEUT", "{MASC/NEUT}"}:
        #         tags.discard(gender)
        if "V.PTCP" in tags:
            tags.discard("V")
        if "V" in tags:
            tags.discard("FIN")
            if "PST" in tags:
                tags.add("PFV")
            if "IPFV" in tags:
                tags.add("PST")
            if "COND" in tags:
                tags.discard("PRS")
            if "IMP" in tags:
                tags.add("POS")
                tags.discard("PRS")
        if tags == set("MASC;PST;SG;V;V.PTCP".split(";")):
            tags = {"PST", "V.PTCP"}
        if tags == set("V;V.MSDR".split(";")):
            tags = set("PRS;V.PTCP".split(";"))
        if {"IPFV", "SBJV"} < tags:
            tags.remove("IPFV")
        return ";".join(tags)


class CzechTranslator(Translator):
    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        if "ADJ" in tags:
            tags.discard("POS")
        if "N" in tags:
            tags.discard("POS")
            tags.discard("INAN")
            tags.discard("ANIM")
            for gender in {"MASC", "FEM", "NEUT", "{MASC/NEUT}"}:
                if gender in tags:
                    tags.remove(gender)
        if "V" in tags:
            tags.discard("ACT")
            tags.discard("FIN")
            tags.discard("POS")
        return ";".join(tags)


class DanishTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        assert "ADJ" not in tags

    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        if "V" in tags:
            tags.discard("FIN")
        return ";".join(tags)


class DutchTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        assert "N" not in tags


class EnglishTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        assert "V" in tags or "V.PTCP" in tags or "V.CVB" in tags or "V.MSDR" in tags

    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        tags.discard("FIN")
        tags.discard("IND")
        if tags == {"V", "PRS"}:
            tags = {"V", "NFIN"}
        if tags == {"V", "V.MSDR"}:
            tags = {"PRS", "V", "V.PTCP"}
        if "V" in tags:
            tags.discard("PASS")
        return ";".join(tags)


class EstonianTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        assert "ADJ" not in tags


class FinnishTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        assert tags != set("ADJ;GEN;SG".split(";"))
        assert tags != set("ADJ;GEN;PL".split(";"))
        assert "0" not in tags

    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        if "V" in tags:
            if "FIN" in tags:
                tags.remove("FIN")
                tags.add("POS")
        if tags == set("NOM;PASS;SG;V;V.PTCP".split(";")):
            tags = set("PASS;PST;V.PTCP".split(";"))
        if tags == set("ACT;NOM;SG;V;V.PTCP".split(";")):
            tags.remove("NOM")
            tags.remove("SG")
            tags.remove("V")
            tags.add("PST")
        if tags == set("ACT;NFIN;SG;V".split(";")):
            tags.remove("ACT")
            tags.remove("SG")
        return ";".join(tags)


class FrenchTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        assert "V" in tags or "V.PTCP" in tags or "V.CVB" in tags or "V.MSDR" in tags

    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        # if "N" in tags:
        #     for gender in {"MASC", "FEM", "NEUT", "{MASC/NEUT}"}:
        #         tags.discard(gender)
        if "V.PTCP" in tags:
            tags.discard("V")
            tags.discard("MASC")
            tags.discard("FEM")
            tags.discard("SG")
            tags.discard("PL")
        if "V" in tags:
            tags.discard("FIN")
            if "PST" in tags:
                tags.add("PFV")
            if "IPFV" in tags:
                tags.add("PST")
            if "COND" in tags:
                tags.discard("PRS")
            if "IMP" in tags:
                tags.add("POS")
                tags.discard("PRS")
        if tags == set("MASC;PST;SG;V;V.PTCP".split(";")):
            tags = {"PST", "V.PTCP"}
        if tags == set("V;V.MSDR".split(";")):
            tags = set("PRS;V.CVB".split(";"))
        return ";".join(tags)


class GermanTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        assert "V" in tags or "N" in tags or "V.PTCP" in tags or "V.CVB" in tags or "V.MSDR" in tags
        # assert tags != {"N"}
        # assert tags != {"V"}

    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        for gender in {"MASC", "FEM", "NEUT", "{MASC/NEUT}"}:
            if gender in tags:
                tags.remove(gender)
        tags.discard("FIN")
        if tags == {"V", "V.PTCP"}:
            tags = {"PST", "V.PTCP"}
        return ";".join(tags)
# translators[get_lang("German")] = GermanTranslator


class HebrewTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        assert "ADJ" not in tags

    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        for gender in {"MASC", "FEM", "NEUT", "{FEM/MASC}"}:
            if gender in tags:
                tags.remove(gender)
        if "V.PTCP" in tags:
            tags.discard("V")
        if "V" in tags:
            tags.discard("ACT")
            tags.discard("POS")
        if "N" in tags:
            if len(tags) == 2:
                if "SG" in tags or "PL" in tags:
                    tags.add("NDEF")

        return ";".join(tags)


class HungarianTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        assert "ADJ" not in tags

    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        tags.discard("FIN")
        tags.discard("ACT")
        if "NFIN" in tags:
            tags.discard("PRS")
        # if "IN+ABL" in tags:
        #     tags.discard("IN+ABL")
        #     tags.add("ON+ABL")
        # if "IN+ESS" in tags:
        #     tags.discard("IN+ESS")
        #     tags.add("ON+ESS")
        # if "IN+ALL" in tags:
        #     tags.discard("IN+ALL")
        #     tags.add("ON+ALL")
        return ";".join(tags)


class ItalianTranslator(Translator):
    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        # if "N" in tags:
        #     for gender in {"MASC", "FEM", "NEUT", "{MASC/NEUT}"}:
        #         tags.discard(gender)
        if "V.PTCP" in tags:
            tags.discard("V")
            tags.discard("MASC")
            tags.discard("FEM")
            tags.discard("SG")
            tags.discard("PL")
        if "V" in tags:
            tags.discard("FIN")
            if "PST" in tags:
                tags.add("PFV")
            if "IPFV" in tags:
                tags.add("PST")
            if "COND" in tags:
                tags.discard("PRS")
        if tags == set("MASC;PST;SG;V;V.PTCP".split(";")):
            tags = {"PST", "V.PTCP"}
        if tags == set("V;V.MSDR".split(";")):
            tags = set("PRS;V.CVB".split(";"))
        return ";".join(tags)


class LatinTranslator(Translator):
    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        if "N" in tags:
            for gender in {"MASC", "FEM", "NEUT", "{MASC/NEUT}"}:
                tags.discard(gender)
        if "V" in tags:
            tags.discard("ACT")
            tags.discard("FIN")
        return ";".join(tags)


class LatvianTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        assert tags != set("3;IND;PRS;V".split(";"))
        assert tags != set("3;IND;PST;V".split(";"))
        assert tags != set("3;IND;FUT;V".split(";"))
        assert "ESS" not in tags

    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        if "V" in tags:
            tags.discard("FH")
            tags.discard("POS")
            tags.discard("NEG")
            tags.discard("ACT")
            tags.discard("FIN")
            tags.discard("REFL")
        if "N" in tags:
            for gender in {"MASC", "FEM", "NEUT", "{MASC/NEUT}"}:
                tags.discard(gender)
        if tags == set("COND;V".split(";")):
            tags.add("PRS")
        return ";".join(tags)


class Norwegian_BokmaalTranslator(Translator):
    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        tags.discard("IND")
        tags.discard("FIN")
        return ";".join(tags)


class Norwegian_NynorskTranslator(Translator):
    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        tags.discard("IND")
        tags.discard("FIN")
        return ";".join(tags)


class PolishTranslator(Translator):
    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        if "N" in tags:
            for gender in {"MASC", "FEM", "NEUT"}:
                tags.discard(gender)
            tags.discard("INAN")
            tags.discard("HUM")
            tags.discard("NHUM")
        if "ADJ" in tags:
            if "PL" in tags:
                for gender in {"MASC", "FEM", "NEUT"}:
                    tags.discard(gender)
            tags.discard("HUM")
            tags.discard("INAN")
        if set("IPFV;NFIN;V".split(";")) == tags:
            tags.remove("IPFV")
        if set("PFV;NFIN;V".split(";")) == tags:
            tags.remove("PFV")
        if "V" in tags:
            tags.discard("ACT")
            tags.discard("FIN")
            tags.discard("IND")
            tags.discard("IPFV")
        return ";".join(tags)


class PortugueseTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        assert "V" in tags or "V.PTCP" in tags or "V.CVB" in tags or "V.MSDR" in tags

    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        if "V.PTCP" in tags:
            tags.discard("V")
            if "PASS" in tags:
                tags.remove("PASS")
                tags.add("PST")
            if "PRS" not in tags:
                tags.add("PST")
            if (cols.form.endswith("do") or cols.form.endswith("to")) and tags == set("PST;V.PTCP".split(";")):
                tags.add("MASC")
                tags.add("SG")
        if tags == {"V", "V.MSDR"}:
            tags = {"V.PTCP", "PRS"}
        if "V" in tags:
            tags.discard("FIN")
            if "PST" in tags and "IPFV" not in tags:
                tags.add("PFV")
            if "IPFV" in tags:
                tags.add("PST")
            if cols.form.endswith("ram") and tags == set("3;IND;PL;V".split(";")):
                tags.add("PFV")
                tags.add("PST")
            tags.discard("PASS")
            if "PST+PRF" in tags:
                tags.add("PST")
                tags.add("PRF")
                tags.remove("PST+PRF")
        return ";".join(tags)


class RomanianTranslator(Translator):
    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        if "V" in tags:
            tags.discard("FIN")
        if "{ACC/NOM}" in tags:
            tags.remove("{ACC/NOM}")
            tags.add("NOM/ACC")
        if "N" in tags:
            for gender in {"MASC", "FEM", "NEUT", "{MASC/NEUT}"}:
                tags.discard(gender)
        if {"V", "PST", "IND"} < tags:
            tags.add("PFV")
        return ";".join(tags)


class SlovenianTranslator(Translator):
    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        if "N" in tags:
            for gender in {"MASC", "FEM", "NEUT", "{MASC/NEUT}"}:
                tags.discard(gender)
            tags.discard("ANIM")
        return ";".join(tags)


class SpanishTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        assert "V" in tags or "V.PTCP" in tags or "V.CVB" in tags or "V.MSDR" in tags

    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        tags.discard("FIN")
        if "AUX" in tags:
            tags.remove("AUX")
            tags.add("V")
        if {"V", "V.PTCP"} < tags:
            tags.remove("V")
        if {"V", "V.MSDR"} == tags:
            tags = {"PRS", "V.CVB"}
        if "PST" in tags and "V.PTCP" not in tags:
            tags.add("PFV")
        if {"IND", "IPFV"} < tags:
            tags.add("PST")
        if "IMP" in tags:
            tags.add("POS")
        if {"IPFV", "SBJV"} < tags:
            tags.remove("IPFV")
            tags.add("PST")
            if cols.form[-2:] == "ra" or cols.form[-3:] == "ran":
                tags.add("LGSPEC1")
        return ";".join(tags)
# translators[get_lang("Spanish")] = SpanishTranslator


class SwedishTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        # assert "CMPR" not in tags
        pass

    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        tags.discard("FIN")
        if "ADJ" in tags:
            tags.discard("NOM")
            if "V.PTCP" in tags:
                tags.remove("V.PTCP")
                tags.discard("PST")
                tags.discard("PRS")
        if tags == {"ADJ", "PL"}:
            tags.add("INDF")
        if "N" in tags:
            tags.discard("MASC+FEM")
            tags.discard("NEUT")
        if tags == {"ACT", "SUP", "V"} or tags == {"PASS", "SUP", "V"}:
            tags.remove("SUP")
            tags.remove("V")
            tags.add("V.CVB")
        if tags == {"ADJ", "DEF", "SG"}:
            tags = {"ADJ", "DEF"}
        if {"IND", "PRS", "V"} == tags:
            tags.add("ACT")
        if {"ACT", "IMP", "V"} == tags:
            tags.remove("ACT")
        return ";".join(tags)


class TurkishTranslator(Translator):
    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        if "N" in tags:
            tags.discard("3")
        return ";".join(tags)

    # def lgspec_assert(self, cols, tags):
    #     assert "ESS" not in tags


class UkrainianTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        # assert "DET" not in tags
        pass

    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        if "N" in tags:
            for gender in {"MASC", "FEM", "NEUT", "{MASC/NEUT}"}:
                if gender in tags:
                    tags.remove(gender)
        if "N" in tags:
            tags.discard("INAN")
            tags.discard("ANIM")
        if tags >= {"NFIN", "V"}:
            tags.discard("IPFV")
            tags.discard("PFV")
        if "V" in tags:
            for tag in "FIN;IND;PFV;IPFV".split(";"):
                tags.discard(tag)
        if "V.CVB" in tags:
            tags.discard("V")
        return ";".join(tags)


class UrduTranslator(Translator):
    def lgspec_assert(self, cols, tags):
        # assert "PART" not in tags
        assert 'ADJ' not in tags

    def lgspec_modify(self, cols, um):
        tags = set(um.split(";"))
        for gender in {"MASC", "FEM", "NEUT", "{MASC/NEUT}"}:
            if gender in tags:
                tags.remove(gender)
        if {"N", "SG"} <= tags or {"N", "PL"} <= tags or "PROPN" in tags:
            tags.discard("3")
        return ";".join(tags)


translators = dict()
for language in languages:
    name = language.name
    try:
        translators[language] = getattr(__import__(__name__),
                                        "".join(name.replace("-", "_")) + "Translator")
    except (NameError, AttributeError):
        pass
