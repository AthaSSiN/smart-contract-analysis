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
        return [1, file_name]

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
        return [len(codes.keys()), file_name]

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
                temp_v = '.'.join(v.split('.')[:2])

                for ver in versions:
                    if temp_v in ver:
                        v = ver
                        break
            elif ">=" in v:
                v = versions[0]
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
        source_file = sys.argv[2]
        n = 1
    elif sys.argv[1] == "-d":
        n, source_file = download_contract(sys.argv[2])
    elif sys.argv[1] == "-m":
        n = 2
        source_file = sys.argv[2]
    
    # flatten contract to run slither and mythril    

    v = get_version(source_file)
    if v == '':
        v = "0.8.17"
    print("Solidity version", v)

    if n > 1:
        print("Flattening Contract")

        c = f'docker run -v {os.getcwd()}:/tmp -w /tmp trailofbits/eth-security-toolbox -c'.split()
        c.append(f'solc-select install {v}; solc-select use {v} ; slither-flat /tmp/{source_file} --strategy OneFile --dir /tmp/{os.path.dirname(source_file)}')
        _ = subprocess.run(c, stdout = subprocess.PIPE)

        filename = '/tmp/crytic-export/flattening/export.sol'

    else:
        print("Single file contract")

        filename = f'/tmp/{source_file}'

    # run slither
       
    os.makedirs(f"analysis/{'/'.join(source_file.split('/')[:-1])}", exist_ok = True)

    print("Running slither")

    c = f'docker run -v {os.getcwd()}:/tmp -w /tmp trailofbits/eth-security-toolbox -c'.split()
    c.append(f'solc-select install {v}; solc-select use {v} ; slither {filename}')
    out = subprocess.run(c, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

    out_file = f"analysis/{source_file}.slither.txt"

    f = open(out_file, "w")
    f.write(out.stdout.decode('UTF-8'))
    f.close()


    # run mythril

    print("Running mythril")

    if len(sys.argv) == 5:
        c = f"docker run -v {os.getcwd()}:/tmp mythril/myth analyze {filename} --solv {v} --execution-timeout {sys.argv[3]} --max-depth {sys.argv[4]}".split()
    else:
        c = f"docker run -v {os.getcwd()}:/tmp mythril/myth analyze {filename} --solv {v}".split()

    out = subprocess.run(c, stdout = subprocess.PIPE)

    out_file = f"analysis/{source_file}.mythril.txt"

    f = open(out_file, "w")
    f.write(out.stdout.decode('UTF-8'))
    f.close()

    # run SMTChecker
    if v == "0.8.17":

        print("Running SMTChecker")
        c = f'docker run -v {os.getcwd()}:/tmp -w /tmp est2 -c'.split()

        if len(sys.argv) >= 4:
            timeout = int(sys.argv[3]) * 1000
        else:
            timeout = 0
        print(timeout)
        c.append(f"solc {filename} --model-checker-engine all --model-checker-show-unproved --model-checker-timeout {timeout} --model-checker-targets all")
        out = subprocess.run(c, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

        out_file = f"analysis/{source_file}.smtchecker.txt"

        f = open(out_file, "w")
        f.write(out.stdout.decode('UTF-8'))
        f.close()

    else:
        print("SMTChecker not supported for lower solidity versions")

if __name__ == "__main__":
    main()
