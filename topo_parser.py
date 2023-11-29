from argparse import ArgumentParser
from pathlib import Path
import pickle
import re
import multiprocessing
from datetime import datetime, timedelta

STORE_FILE = "store.pkl"
OUTPUT_FILE = "output.txt"


class Device:

    def __init__(self, dev_data, dev_type=None):

        self.name = re.search(r'"([^"]*)"', dev_data[4]).group(1)
        self.devid = dev_data[1].split("=")[1]
        self.sysimgguid = dev_data[2].split("=")[1]
        self.caguid = dev_data[3].split("=")[1]
        self.connections = self.__get_connections(dev_data[5:])
        self.type = dev_type

    def __get_connections(self, data: list) -> list:
        """
        Get all device connections from the data block
        :param data: Information lines about the device from the topology file
        :return: connections
        """
        connections = []
        for connection in data:
            connection_obj = Connection(connection)
            connections.append(connection_obj)
        return connections

    def __str__(self):
        res = "{} {}\n".format(self.type, self.name)
        res += "devid={} sysimgguid={} caguid={}\n".format(self.devid, self.sysimgguid, self.caguid)
        res += f"{''.join(str(connection) for connection in self.connections)}"
        return res


class Host(Device):
    def __init__(self, dev_data):
        super().__init__(dev_data, Host.__name__)

    @staticmethod
    def is_host(line):
        return line.startswith("Ca")


class Switch(Device):
    def __init__(self, dev_data):
        super().__init__(dev_data, Switch.__name__)

    @staticmethod
    def is_switch(line):
        return line.startswith("Switch")


class Connection:

    def __init__(self, line: str):
        self.port_local, \
        self.dev_remote, \
        self.port_remote \
            = self.__get_connection_params(line)

    def __get_connection_params(self, line: str) -> object:
        """

        :param line:
        :return:
        """
        match = re.search(Connection.search_pattern(), line)
        if match:
            return match.group(1), match.group(3), match.group(4)
        else:
            raise ValueError(f"No match found in string:\n{line}")

    @classmethod
    def search_pattern(cls) -> str:
        return r'(\[\d+\])(\([\w]+\))?\s+"(.*?)"(\[\d+\])(\([\w]+\))?'

    def __str__(self):
        return f" Port {self.port_local} connected to {self.dev_remote} port {self.port_remote}\n"


class Topology:
    PATTERN = {
        "open_line": "vendid=",
        "close_line": ""
    }
    OUTPUT_BEGIN_MSG = "# Topology map generated at {}\n" \
                       "# Source file: {}\n\n"

    def __init__(self, source_file, store_file, output_file):
        self.source_file = source_file
        self.store_file = store_file
        self.output_file = output_file
        self.devices = dict()
        self.start_parse_time = datetime.now()
        self.end_parse_time = None
        self.devices_count = 0
        self.host_count = 0
        self.switch_count = 0

    @staticmethod
    def file_exist_check(file):
        if not file.exists():
            print(f"The target file  doesn't exist: {file}")
            raise SystemExit(1)
        else:
            print(f"- Source file: {Path(file).name}")

    @staticmethod
    def print_parse_progress():
        print("*", end="")

    def print_parsed_info(self):
        print(f"\n  Devices: {self.devices_count}\n" \
              f"  Switches: {self.switch_count}\n" \
              f"  Hosts: {self.host_count}\n" \
              f"  Parsing time: {self.get_parse_time()} sec\n")

    def get_parse_time(self):
        return (self.end_parse_time - self.start_parse_time).total_seconds()

    @staticmethod
    def block_generator(file: str, open_pattern: str, close_pattern: str):
        block_lines = []
        with open(file) as f:
            for line in f:
                if open_pattern in line and not block_lines:
                    block_lines.append(line.strip())
                elif close_pattern == line.strip() and block_lines:
                    yield block_lines
                    block_lines = []
                elif block_lines:
                    block_lines.append(line.strip())
        yield block_lines if block_lines else None

    def run_parse(self):
        """

        :rtype: object
        """
        data_blocks = Topology.block_generator(self.source_file,
                                               self.PATTERN["open_line"],
                                               self.PATTERN["close_line"])
        for data in data_blocks:
            device_obj = self.create_device(data)
            self.devices[device_obj.name] = device_obj
            self.devices_count += 1
            self.print_parse_progress()
        else:
            self.end_parse_time = datetime.now()
            self.print_parsed_info()

    def create_device(self, dev_data: list):
        if Host.is_host(dev_data[4]):
            self.host_count += 1
            return Host(dev_data)
        elif Switch.is_switch(dev_data[4]):
            self.switch_count += 1
            return Switch(dev_data)
        else:
            raise ValueError("Unrecognized device type")

    @staticmethod
    def dump_pkl_to_file(topology, file: str):
        print(f"- Dump topology to {file}\n")
        with open(file, 'wb') as f:
            pickle.dump(topology, f)

    @staticmethod
    def load_pkl_from_file(file: str):
        print(f"- Load topology from {file}")
        with open(file, 'rb') as f:
            return pickle.load(f)

    def run_print_parsed_topology(self) -> None:
        with open(self.output_file, 'w') as f:
            f.write(self.OUTPUT_BEGIN_MSG.format(self.start_parse_time, Path(self.source_file).name))
            f.write('\n'.join(str(device) for device in self.devices.values()))


def main():
    def get_args_parser():
        parser = ArgumentParser(description='Parses file, finds, and prints all connections in the network')
        parser.add_argument("--file", '-f',
                            type=Path,
                            required=False,
                            help='parse topofile.topo')
        parser.add_argument("--print", '-p',
                            required=False,
                            action='store_true',
                            help='print parsed topology')
        parser.add_argument("--exit", '-e',
                            action='store_true',
                            required=False,
                            help='print usage and exit')
        return parser

    def parse_topology(source_file, store_file, output_file):
        topo = Topology(source_file, store_file, output_file)
        topo.file_exist_check(source_file)
        topo.run_parse()
        topo.dump_pkl_to_file(topo, store_file)
        return topo

    def print_parsed_topology(store_file, topo):
        if not topo:
            topo = Topology.load_pkl_from_file(store_file)
        multiprocessing.Process(target=topo.run_print_parsed_topology).start()

    parser = get_args_parser()
    input_args = None
    topology = None

    while True:
        args, unknown = parser.parse_known_args(input_args)

        if args.file:
            print("- Parse topology file ")
            topology = parse_topology(args.file, STORE_FILE, OUTPUT_FILE)
        if args.print:
            print_parsed_topology(STORE_FILE, topology)
            print(f"\n- Print result in {OUTPUT_FILE}\n")
        if args.exit:
            break
        if unknown:
            parser.print_help()

        timedelta(seconds=2)
        input_args = input(">> ").split()


if __name__ == "__main__":
    main()
