## Topo Parser
Topo Parser is a Python program for parsing and printing network topology. 

## Usage
```bash
python topo_parser.py <options>
```
## Input options

```bash
–h Print usage information

–f <topofile> Parse a topology file

–p Print the parsed topology after the program is running

–e exit the program

```

## Usage Examle
```bash
python topo_parser.py -h  # Print usage and exit
````

```bash
python topo_parser.py -f topofile.topo  # Parse topofile.topo
```
```bash
python topo_parser.py -f topofile.topo -p  # Parse and print topology
```
##Installation
To use Topo Parser, follow these steps:
```bash
pip install -r requirements.txt
```