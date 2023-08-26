from pathlib import Path
from typing import List, Tuple

from .languages import LanguageCoding

# These must be pathlib Path objects.
# Easy way: Path('whatever/my/path/is')
_ROOT = Path("/Users/arya/Desktop/UD_UM") / "data" / "raw"
UM_FOLDER = _ROOT / "UM"
UD_FOLDER = _ROOT / "UD"
UD2UM_FILE = Path(".") / "UD-UniMorph.tsv"


class FileGetter:
    @staticmethod
    def get(language: LanguageCoding, convert=False) -> Tuple[Path, List[Path]]:
        um_file = UM_FOLDER / f"{language.um}-master" / f"{language.um}"
        lang_folder = UD_FOLDER / f"UD_{language.name}-master"
        print(lang_folder)
        ud_files = list(lang_folder.glob(f"{language.ud}-ud-*.conllu"))
        FileGetter._check_inputs(um_file, ud_files, convert)
        return um_file, ud_files

    @staticmethod
    def _check_inputs(um_file: Path, ud_files: List[Path], skip_um: bool) -> None:
        if not skip_um:
            FileGetter._validate_file(um_file)
        if not ud_files:
            print(f"No useful things in {UD_FOLDER}")
        for file in ud_files:
            FileGetter._validate_file(file)

    @staticmethod
    def _validate_file(file: Path) -> None:
        assert file.is_file(), file


def output_filepath(conllu: Path) -> Path:
    return conllu.with_name(conllu.name.replace("-ud-", "-um-"))
