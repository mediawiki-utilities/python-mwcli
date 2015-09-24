import sys
import traceback
from importlib import import_module


HELP = """
{description}

{utilities}

Usage:
    {package_name} -h | --help
    {package_name} <utility> [-h | --help]

Options:
    -h | --help  Prints this documentation
    <utility>    The name of the utility to run
"""

USAGE = """Usage:
    {package_name} -h | --help
    {package_name} <utility> [-h | --help]
"""


class Router:

    def __init__(self, package_name, description, utilities):
        self.package_name = package_name
        self.description = description
        self.utilities = utilities

    def main(self):

        if len(sys.argv) < 2:
            sys.stderr.write(self.format_usage())
            sys.exit(1)
        elif sys.argv[1] in ("-h", "--help"):
            sys.stderr.write(self.format_help())
            sys.exit(1)
        elif sys.argv[1][:1] == "-":
            sys.stderr.write(self.format_usage())
            sys.exit(1)

        module_name = sys.argv[1]
        if module_name in self.utilities:
            try:
                module = import_module(".utilities." + module_name,
                                       package=self.package_name)
            except ImportError:
                sys.stderr.write(traceback.format_exc())
                sys.stderr.write("Could not load utility {0}.\n"
                                 .format(module_name))
                sys.exit(1)

            module.main(sys.argv[2:])
        else:
            sys.stderr.write("{0} not available.\n".format(module_name))
            sys.exit(1)

    def format_help(self):
        return HELP.format(package_name=self.package_name,
                           description=self.description,
                           utilities=self.format_utilities())

    def format_utilities(self):
        return "\n".join("* {0} -- {1}".format(*u)
                         for u in self.utilities.items())

    def format_usage(self):
        return USAGE.format(package_name=self.package_name,
                            description=self.description,
                            utilities=self.format_utilities)
