#!/bin/bash

curl https://api.github.com/repos/ethereum/solidity/releases?per_page=1000 | jq -r '.[].tag_name' > versions_list.txt
version=`cat $1 | grep pragma -m 1`
echo $version
v=""
if grep -q "<=" <<< "$version"
then
	v=`echo $version | grep -oP '(?<=\<\=)\d+\.\d+\.\d+'`
elif grep -q "<" <<< "$version"
then	
	tv=`echo $version | grep -oP '(?<=\<)\d+\.\d+\.\d+'`
	v=`cat versions_list.txt | grep "$tv" -A1 | tail -n 1`

	if grep -q "preview" <<< "$v"
	then
		v=`cat versions_list.txt | grep "$v" -A1 | tail -n 1`
	fi
elif grep -q "\^" <<< "$version"
then	
	v=`echo $version | grep -oP '(?<=\^)\d+\.\d+\.\d+'`
else
	v=`echo $version | grep -oP '\d+\.\d+\.\d+'`
fi

echo "Using solidity version $v"
docker run -v $(pwd):/tmp mythril/myth analyze /tmp/"$1" --solv $v


