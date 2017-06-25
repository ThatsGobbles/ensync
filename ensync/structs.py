import typing as typ


class SourceFileRecord(typ.NamedTuple):
    root_dir_path: str
    inter_dir_path: str
    audio_file_name: str
    album_art_file_name: str
