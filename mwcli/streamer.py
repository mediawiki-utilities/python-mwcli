import json
import logging
import sys
from multiprocessing import cpu_count

import docopt
import para

from . import files


def read_json(f):
    return (json.loads(l) for l in f)

def no_extra_args(args):
    return {}

class Streamer:

    def __init__(self, doc, name, a2b, process_args=no_extra_args, 
                 file_reader=read_json):
        self.doc = doc
        self.logger = logging.getLogger(name)
        self.a2b = a2b
        self.process_args = process_args
        self.file_reader = file_reader

    def main(self, argv=None):
        args = docopt.docopt(self.doc, argv=argv)

        logging.basicConfig(
            level=logging.INFO if not args['--debug'] else logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
        )

        if len(args['<input-file>']) == 0:
            paths = [sys.stdin]
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

            docs = self.a2b(input, verbose=verbose,
                            **kwargs)

            if output_dir == None:
                yield from docs
            else:
                new_path = files.output_dir_path(path, output_dir, compression)
                writer = files.writer(new_path)
                for doc in docs:
                    json.dump(doc, writer)
                    writer.write("\n")

        for doc in para.map(process_path, paths, mappers=threads):
            json.dump(doc, sys.stdout)
            sys.stdout.write("\n")
