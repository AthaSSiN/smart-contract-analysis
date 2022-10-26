## Installation

Run the install script to install

```bash
./install.sh
```

## Running the test suite

```bash
python3 entry.py -f test_suite
```

## Running on a csv

If the csv contains addresses, the script can download the contracts at those addresses and run the tools on them.
The addresses have to be in the 2nd column

```bash
python3 entry.py -d path_to_csv
```
