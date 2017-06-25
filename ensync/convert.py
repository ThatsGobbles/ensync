import os
import os.path
import typing as typ
import pprint

import pydub
import pydub.utils

import ensync.structs as nstc
import ensync.logging as nlog


logger = nlog.get_logger(__name__)


def ensure_directories(desired_dir_path: str):
    os.makedirs(desired_dir_path, exist_ok=True)


def convert(dst_root_dir_path: str
            , src_records: typ.Iterable[nstc.SourceFileRecord]
            , output_format='mp3'
            ):
    for src_record in src_records:
        # Unpack from source record.
        src_root_dir_path = src_record.root_dir_path
        src_inter_dir_path = src_record.inter_dir_path
        src_audio_file_name = src_record.audio_file_name
        src_album_art_file_name = src_record.album_art_file_name

        src_audio_file_path = os.path.join(src_root_dir_path, src_inter_dir_path, src_audio_file_name)
        src_album_art_file_path = None
        if src_album_art_file_name:
            src_album_art_file_path = os.path.join(src_root_dir_path, src_inter_dir_path, src_album_art_file_name)

        logger.debug('Processing source file: {}'.format(src_audio_file_path))

        # Figure out what the corresponding destination file would look like.
        file_stem, _ = os.path.splitext(src_audio_file_name)

        # Create destination records.
        dst_inter_dir_path = src_inter_dir_path
        dst_audio_file_name = file_stem + '.mp3'

        dst_audio_dir_path = os.path.join(dst_root_dir_path, dst_inter_dir_path)
        dst_audio_file_path = os.path.join(dst_audio_dir_path, dst_audio_file_name)

        os.makedirs(dst_audio_dir_path, exist_ok=True)

        logger.debug('Destination file path: {}'.format(dst_audio_file_path))

        # Test if the source file is newer than the destination file, if the destination exists.
        if os.path.exists(dst_audio_file_path):
            logger.info('Destination file path {} already exists, checking mod times'.format(dst_audio_file_path))
            src_audio_file_stat = os.stat(src_audio_file_path)
            dst_audio_file_stat = os.stat(dst_audio_file_path)
            if dst_audio_file_stat.st_size > 0 and src_audio_file_stat.st_mtime < dst_audio_file_stat.st_mtime:
                logger.info('Destination file path {} more recent than source, skipping'.format(dst_audio_file_path))
                continue

            logger.info('Destination file path {} outdated, deleting and reconverting'.format(dst_audio_file_path))
            os.unlink(dst_audio_file_path)

        # Get channel and sample rate info from source file.
        src_audio_file_info = pydub.utils.mediainfo(src_audio_file_path)
        pprint.pprint(src_audio_file_info)
        src_audio_file_frame_rate = src_audio_file_info['sample_rate']
        src_audio_file_num_channels = src_audio_file_info['channels']
        src_audio_file_sample_width = src_audio_file_info['bits_per_raw_sample']

        # Do the conversion.
        logger.debug(f'Converting audio file {src_audio_file_path}')
        src_audio_data = pydub.AudioSegment.from_file(src_audio_file_path
                                                      , format='flac'
                                                      , channels=src_audio_file_num_channels
                                                      , frame_rate=src_audio_file_frame_rate
                                                      , sample_width=src_audio_file_sample_width
                                                      )
        src_audio_data.export(dst_audio_file_path, format=output_format, cover=src_album_art_file_path)
