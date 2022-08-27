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
        source_file = file_name

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
                source_file = file_name
                flag = 1

    return source_file

def get_version(source_file):

    versions_info = requests.get("https://api.github.com/repos/ethereum/solidity/releases", params = {"per_page" : "1000"}).json()
    versions = [v["tag_name"] for v in versions_info if "preview" not in v["tag_name"]]

    v = ""
    f = open(source_file, "r")
    for line in f.readlines():
        if "pragma solidity" in line:

            v = line
            if "<=" in v:
                v = "v" + re.findall("(?<=\<\=)\d+\.\d+\.\d+", line)[0]
            elif "<" in v:
                v = "v" + re.findall("(?<=\<)\d+\.\d+\.\d+", line)[0]
                v = versions[versions.index(v) + 1]
            elif "^" in v:
                v = "v" + re.findall("(?<=\^)\d+\.\d+\.\d+", line)[0]
            else:
                v = "v" + re.findall("\d+\.\d+\.\d+", line)[0]
            
            break
    f.close()

    return v

def main():

    if sys.argv[1] == "-f":
        source_file = sys.argv[2]
        v = get_version(source_file)
    elif sys.argv[1] == "-d":
        source_file = download_contract(sys.argv[2])
        v = get_version(source_file)

    if len(sys.argv) == 4:
        c = f"docker run -v {os.getcwd()}:/tmp mythril/myth analyze /tmp/{source_file} --solv {v} --max-depth {sys.argv[3]} -o json".split()
    elif len(sys.argv) == 5:
        c = f"docker run -v {os.getcwd()}:/tmp mythril/myth analyze /tmp/{source_file} --solv {v} --max-depth {sys.argv[3]} --execution-timeout {sys.argv[4]} -o json".split()
    else:
        c = f"docker run -v {os.getcwd()}:/tmp mythril/myth analyze /tmp/{source_file} --solv {v} -o json".split()

    out = subprocess.run(c, stdout = subprocess.PIPE)

    out_file = "analysis/" + source_file[:-3] + "json"
    os.makedirs(os.path.dirname(out_file), exist_ok = True)

    f = open(out_file, "w")
    f.write(out.stdout.decode('UTF-8'))
    f.close()

if __name__ == "__main__":
    main()
