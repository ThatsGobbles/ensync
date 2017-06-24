import typing as typ
import os
import os.path
import itertools as it

import ensync.structs as nstc


def find_source_files(root_dir: str
                      , file_name_reg: typ.Pattern
                      , whitelist_entry_reg: typ.Pattern=None
                      , blacklist_entry_reg: typ.Pattern=None
                      , album_art_name_reg: typ.Pattern=None
                      ) -> typ.Iterable[nstc.SourceFileRecord]:
    for dir_path, subdir_names, file_names in os.walk(root_dir):
        # Check if this directory is even worth traversing.
        skip = False
        skip |= (whitelist_entry_reg is not None
                 and not any(whitelist_entry_reg.match(x) for x in it.chain(file_names, subdir_names))
                 )
        skip |= (blacklist_entry_reg is not None
                 and any(blacklist_entry_reg.match(x) for x in it.chain(file_names, subdir_names))
                 )
        if skip:
            # TODO: Process further down?
            subdir_names[:] = []
            continue

        # Find files inside this directory we care about.
        sorted_file_names = sorted(file_names)
        audio_files = (file_name for file_name in sorted_file_names if file_name_reg.match(file_name))

        album_art_file = None

        if album_art_name_reg is not None:
            for file_name in sorted_file_names:
                if album_art_name_reg.match(file_name):
                    album_art_file = file_name

        for audio_file in audio_files:
            audio_file_path = os.path.join(dir_path, audio_file)
            stat = os.stat(audio_file_path)
            mod_time = stat.st_mtime
            record = nstc.SourceFileRecord(root_dir_path=root_dir
                                           , inter_path=os.path.relpath(dir_path, start=root_dir)
                                           , audio_file_name=audio_file
                                           , album_art_file_name=album_art_file
                                           , mod_time=mod_time
                                           )
            yield record
