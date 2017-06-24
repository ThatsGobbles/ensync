import re

import click

import ensync.discovery as ndis


class RegexPatternType(click.ParamType):
    name = 'regex'

    def __init__(self, ignore_case=False):
        super().__init__()
        self.ignore_case = ignore_case

    def convert(self, value, param, ctx):
        try:
            pattern = value
            r = re.compile(pattern=pattern, flags=(0 if not self.ignore_case else re.IGNORECASE))
            return r
        except re.error:
            self.fail("'{}' is not a valid regular expression".format(value), param, ctx)


@click.command()
@click.argument('src-root-dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True))
@click.argument('dst-root-dir', type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True))
@click.argument('input-regex', type=RegexPatternType())
@click.option('--album-art-regex', type=RegexPatternType())
@click.option('--whitelist-dir-file-regex', type=RegexPatternType())
@click.option('--blacklist-dir-file-regex', type=RegexPatternType())
def cli(src_root_dir, dst_root_dir, input_regex, album_art_regex, whitelist_dir_file_regex, blacklist_dir_file_regex):
    click.echo('Root dir is {}'.format(src_root_dir))
    click.echo('Input regex is {}'.format(input_regex))
    click.echo('Album art regex is {}'.format(album_art_regex))

    finder = ndis.find_source_files(root_dir=src_root_dir
                                    , file_name_reg=input_regex
                                    , album_art_name_reg=album_art_regex
                                    , whitelist_entry_reg=whitelist_dir_file_regex
                                    , blacklist_entry_reg=blacklist_dir_file_regex
                                    )

    for entry in finder:
        click.echo(entry)
