"""
Convert Universal Dependencies morphology annotations to UniMorph.
"""

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Iterable, List, Tuple

from termcolor import cprint

from languages import languages, LanguageCoding, get_lang
from paths import FileGetter, output_filepath
from translator import Translator, translators
from um_reader import unimorph
from utils import CoNLLRow, is_conll_useless, ud_iterator


class EvaluationInstance():
    def __init__(self, language: LanguageCoding, clever=False, replace_feats=False, print_good=False) -> None:
        self.language = language
        self.um_file, self.ud_files = FileGetter.get(language, replace_feats)
        translator_class = translators.get(language, Translator)
        self.translator = translator_class(clever, replace_feats)
        self.print_good = print_good
        # print(self.translator)

        if not replace_feats:
            self.tags, self.lemmas = unimorph(self.um_file)

    def translate(self, source: str, output_all=False) -> CoNLLRow:
        if is_conll_useless(source):
            if output_all:
                return source
            else:
                return
        record = CoNLLRow.make(source)
        updated = self.translator.translate(record)
        if output_all:
            return "\t".join(updated)
        else:
            return updated

    def evaluate(self) -> None:
        scores = []
        for file in self.ud_files:
            score = self._evaluate(file)
            scores.append(score)
            print(file.name, score)
        # Calculate recall.
        good_counts, counts = zip(*scores)
        print(f"Average for {self.language.name}:", sum(good_counts) / (sum(counts) or 1) * 100)

    def convert(self) -> None:
        file: Path
        assert self.ud_files
        for file in self.ud_files:
            print(file)
            lines: Iterable[str] = ud_iterator(file)
            translations = [self.translate(line, output_all=True) for line in lines]
            with open(output_filepath(file), 'w') as f:
                for line in translations:
                    print(line, file=f)

    def score_translation(self, t: CoNLLRow) -> Tuple[int, int]:
        good_count = bad_count = count = 0
        try:
            tag = t.misc
            assert t.form in self.tags
            token_bundle = set(tag.split(";"))
            type_bundles = self.tags[t.form]
            assert t.lemma in self.lemmas[t.form]
            self.translator.lgspec_assert(t, token_bundle)
            if token_bundle in type_bundles:
                good_count += 1
                if self.print_good:
                    cprint(f"{(t.form):20}\t{(';'.join(sorted(token_bundle))):20}\t{str([';'.join(sorted(tags)) for tags in type_bundles]):40}", 'green')
            else:
                cprint(f"{(t.form):20}\t{(';'.join(sorted(token_bundle))):20}\t{str([';'.join(sorted(tags)) for tags in type_bundles]):40}", 'red')
                bad_count += 1
            count += 1
        except AssertionError:
            pass
        assert good_count + bad_count == count
        return good_count, count

    def recall(self, translations: List[CoNLLRow]) -> Tuple[int, int]:
        good_count = count = 0
        for translation in translations:
            gc, c = self.score_translation(translation)
            good_count += gc
            count += c
        return good_count, count

    def _evaluate(self, file: Path) -> Tuple[int, int]:
        lines: Iterable[str] = ud_iterator(file)
        translations = [self.translate(line) for line in lines]
        translations = [t for t in translations if t is not None]
        recall = self.recall(translations)
        return recall


class FileConverter(EvaluationInstance):
    """docstring for FileConverter"""
    def __init__(self, file: Path, language: LanguageCoding, clever: bool):
        super(FileConverter, self).__init__(language, clever, replace_feats=True)
        self.ud_files = [file]


def parse_args() -> Namespace:
    parser = ArgumentParser(__doc__)
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')

    # create the parser for the "a" command
    replicate = subparsers.add_parser(
        'replicate',
        help='replicate experiments from McCarthy et al. (2018)')
    # parser_a.add_argument('bar', type=int, help='bar help')

    # create the parser for the "b" command
    evaluate = subparsers.add_parser(
        'evaluate',
        help='evaluate a Translator class')
    evaluate.add_argument(
        '-b', "--basic",
        action='store_true',
        help="dumb conversion?"
        )
    evaluate.add_argument(
        '-p', "--print_good",
        action='store_true',
        help="Print good during evaluation, or only bad?"
        )
    evaluate.add_argument(
        '-l', '--langs',
        nargs='+',
        required=True,
        help='languages to convert (e.g. "da eu sp")')

    # create the parser for the "b" command
    convert = subparsers.add_parser(
        'convert',
        help='convert UD files to UniMorph')
    convert.add_argument(
        '-b', "--basic",
        action='store_true',
        help="dumb conversion?"
        )
    convert.add_argument(
        '--ud',
        type=Path,
        help="UD file; warning: this will not use the clever converter")
    convert.add_argument(
        '-l', '--langs',
        nargs='+',
        help='languages to convert (e.g. "da eu sp")')
    return parser.parse_args()


def replicate():
    for language in languages:
        cprint(language.name, attrs={'bold'})
        for clever in [False, True]:
            print("Clever? ", clever)
            instance: EvaluationInstance = EvaluationInstance(language, clever)
            instance.evaluate()


def evaluate(args: Namespace):
    for language_ in args.langs:
        language = get_lang(language_)
        cprint(language.name, attrs={'bold'})

        clever = not args.basic
        instance: EvaluationInstance = EvaluationInstance(language, clever, print_good=args.print_good)
        instance.evaluate()


def convert(args: Namespace):
    for language_ in args.langs:
        language = get_lang(language_)
        cprint(language.name, attrs={'bold'})

        clever = not args.basic
        instance: EvaluationInstance = EvaluationInstance(language, clever, replace_feats=True)
        instance.convert()


def convert_file(args: Namespace):
    assert not args.langs or len(args.langs) == 1
    if args.langs:
        try:
            [language_] = args.langs
            language = get_lang(language_)
        except KeyError:
            cprint(f"Warning: no clever converter exists for {args.ud}", 'cyan')
            language = LanguageCoding(None, None, "")
    else:  # args.langs == None
        cprint(f"Warning: no clever converter exists for {args.ud}", 'cyan')
        language = LanguageCoding(None, None, "")
    cprint(language.name, attrs={'bold'})
    clever = not args.basic

    instance: FileConverter = FileConverter(args.ud, language, clever)
    instance.convert()

def main():
    args = parse_args()
    print(args)
    if args.command == 'replicate':
        replicate()
    elif args.command == 'evaluate':
        evaluate(args)
    elif args.command == 'convert':
        if args.ud:
            convert_file(args)
        else:
            convert(args)
    else:
        raise ValueError


if __name__ == '__main__':
    main()
