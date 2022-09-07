import requests
import json
import os
import sys
import re
import subprocess

def download_contract(address):
    

    params = {"module" : "contract", "action" : "getsourcecode", "address" : address, "apikey" : "653NTJN7RSS3ZKV6QAZIVR9NQUHXR91HKD"}
    r = requests.get("https://api.etherscan.io/api", params = params)

    r = r.json()

    source_file = ""

    if r["result"][0]["SourceCode"][0] != '{':
        file_name = address + "/contract.sol"
        os.makedirs(os.path.dirname(file_name), exist_ok = True)
        code = r["result"][0]["SourceCode"]
        f = open(file_name, "w")
        f.write(code)
        f.close()
        source_file = "contract.sol"
        return [1, source_file]

    else:
        contracts = json.loads(r["result"][0]["SourceCode"][1:-1])
        codes = contracts["sources"]
        flag = 0
        for code in codes.keys():
            file_name = address + "/" + code
            os.makedirs(os.path.dirname(file_name), exist_ok = True)
            f = open(file_name, "w")
            f.write(codes[code]['content'])
            f.close()

            if flag == 0:
                source_file = code
                flag = 1
        return [len(codes.keys()), source_file]

def get_version(source_file):

    versions_info = requests.get("https://api.github.com/repos/ethereum/solidity/releases", params = {"per_page" : "1000"}).json()
    versions = [v["tag_name"][1:] for v in versions_info if "preview" not in v["tag_name"]]

    vm = ""
    f = open(source_file, "r")
    for line in f.readlines():
        if "pragma solidity" in line:

            v = line
            if "<=" in v:
                v = re.findall("(?<=\<\=)\d+\.\d+\.\d+", line)[0]
            elif "<" in v:
                v = re.findall("(?<=\<)\d+\.\d+\.\d+", line)[0]
                v = versions[versions.index(v) + 1]
            elif "^" in v:
                v = re.findall("(?<=\^)\d+\.\d+\.\d+", line)[0]
            else:
                v = re.findall("\d+\.\d+\.\d+", line)[0]
            
            if vm != "":
                vmt = [int(vmi) for vmi in vm.split('.')]
                vt = [int(vi) for vi in v.split('.')]

                if vt > vmt:
                    vm = v

            else:
                vm = v
    f.close()

    return vm

def main():

    if sys.argv[1] == "-f":
        n, source_file = sys.argv[2]
    elif sys.argv[1] == "-d":
        n, source_file = download_contract(sys.argv[2])
        os.chdir(sys.argv[2])
    
    # flatten contract to run slither and mythril    

    v = get_version(source_file)
    print("Solidity version", v)

    if n > 1:
        print("Flattening Contract")

        c = f'docker run -v {os.getcwd()}:/tmp -w /tmp trailofbits/eth-security-toolbox -c'.split()
        c.append(f'solc-select use {v} ; slither-flat /tmp/{source_file} --strategy OneFile')
        _ = subprocess.run(c, stdout = subprocess.PIPE)

        filename = '/tmp/crytic-export/flattening/export.sol'

    else:
        print("Single file contract")

        filename = f'/tmp/{source_file}'

    # run slither
       
    os.makedirs("analysis", exist_ok = True)

    print("Running slither")

    c = f'docker run -v {os.getcwd()}:/tmp -w /tmp trailofbits/eth-security-toolbox -c'.split()
    c.append(f'solc-select use {v} ; slither --json /tmp/analysis/slither.json {filename}')
    _ = subprocess.run(c, stdout = subprocess.PIPE)

    # run mythril

    print("Running mythril")

    if len(sys.argv) == 4:
        c = f"docker run -v {os.getcwd()}:/tmp mythril/myth analyze {filename} --solv {v} --max-depth {sys.argv[3]} -o json".split()
    elif len(sys.argv) == 5:
        c = f"docker run -v {os.getcwd()}:/tmp mythril/myth analyze {filename} --solv {v} --max-depth {sys.argv[3]} --execution-timeout {sys.argv[4]} -o json".split()
    else:
        c = f"docker run -v {os.getcwd()}:/tmp mythril/myth analyze {filename} --solv {v} -o json".split()

    out = subprocess.run(c, stdout = subprocess.PIPE)

    out_file = "analysis/mythril.json"

    f = open(out_file, "w")
    f.write(out.stdout.decode('UTF-8'))
    f.close()

    if sys.argv[1] == "-d":
        os.chdir("..")

if __name__ == "__main__":
    main()
