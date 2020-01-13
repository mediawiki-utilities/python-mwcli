import io
import json
import logging
import sys
from multiprocessing import cpu_count

import docopt
import para
from mwxml import Dump

from . import files


class Streamer:
    @staticmethod
    def read_json(f):
        return (json.loads(l) for l in f)

    @staticmethod
    def read_xml(f):
        return Dump.from_file(f)

    @staticmethod
    def write_json(doc, f):
        f.write(json.dumps(doc))
        f.write("\n")

    @staticmethod
    def write_line(line, f):
        f.write(line)
        f.write("\n")

    @staticmethod
    def no_extra_args(args):
        return {}

    def __init__(self, doc, name, a2b, process_args=None,
                 file_reader=None, line_writer=None):
        self.doc = doc
        self.logger = logging.getLogger(name)
        self.a2b = a2b
        self.process_args = process_args or Streamer.no_extra_args
        self.file_reader = file_reader or Streamer.read_json
        self.line_writer = line_writer or Streamer.write_json

    def main(self, argv=None):
        args = docopt.docopt(self.doc, argv=argv)

        logging.basicConfig(
            level=logging.INFO if not args['--debug'] else logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
        )

        if len(args['<input-file>']) == 0:
            paths = [io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')]
        else:
            paths = [files.normalize_path(p) for p in args['<input-file>']]

        kwargs = self.process_args(args)

        if args['--threads'] == "<cpu_count>":
            threads = cpu_count()
        else:
            threads = int(args['--threads'])

        if args['--output'] == "<stdout>":
            output_dir = None
            self.logger.info("Writing output to stdout.  Ignoring " +
                             "'compress' setting.")
            compression = None
        else:
            output_dir = files.normalize_dir(args['--output'])
            compression = args['--compress']

        verbose = bool(args['--verbose'])

        self.run(paths, threads, kwargs, output_dir, compression, verbose)

    def run(self, paths, threads, kwargs, output_dir, compression, verbose):

        def process_path(path):
            f = files.reader(path)
            input = self.file_reader(f)

            outputs = self.a2b(input, verbose=verbose,
                               **kwargs)

            if output_dir is None:
                yield from outputs
            else:
                new_path = files.output_dir_path(path, output_dir, compression)
                writer = files.writer(new_path)
                for output in outputs:
                    self.line_writer(output, writer)

        for output in para.map(process_path, paths, mappers=threads):
            self.line_writer(output, sys.stdout)
