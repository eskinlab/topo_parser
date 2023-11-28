from argparse import ArgumentParser
from pathlib import Path


TOPOFILE_PATH = Path(r'C:\Users\didge\Downloads\TopologyFiles')
TOPOFILE_NAME = "large_topo_file"
TOPOFILE_NAME = "small_topo_file"

net_map = {
    hosts_start: [],
    switchs: [],
    hosts_end: []
}


def args_parser():
    parser = ArgumentParser(description='Parses file, finds, and prints all connections in the network')
    parser.add_argument("--file", '-f',
                        type=Path,
                        required=False,
                        default=TOPOFILE_PATH / TOPOFILE_NAME,
                        help='parse topofile.topo')

    parser.add_argument("--usage", '-u',
                        type=str,
                        required=False,
                        default="d",
                        help='print usage and exit')

    parser.add_argument("--parsed", '-p',
                        type=str,
                        required=False,
                        help='print parsed topology')

    return parser.parse_args()


def process_usage(line):
    print(line, end="")


def process_parsed(line):
    pass


def main(file, usage=None, parsed=None):

    if not usage or parsed:
        print("Flags are not identified. Use --help")
    else:
        with open(file) as file:
            for line in file:
                if usage:
                    process_usage(line)
                elif parsed:
                    process_parsed(line)


def file_exist_check(file):
    if not file.exists():
        print(f"The target file  doesn't exist: {file}")
        raise SystemExit(1)


if __name__ == "__main__":
    args = args_parser()

    file_exist_check(args.file)
    main(args.file, args.usage, args.parsed)
