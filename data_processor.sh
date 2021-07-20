#!/bin/bash

counter=0

function join_lines {
    local IFS="$1"
    shift
    echo "$*"
}


while IFS= read -r line || [ -n "$line" ]; do
    if [[ -z ${line} ]];
    then
        :
    elif [[ ${line: -1}  != '"' ]]; 
    then
	    to_combine[$counter]=$line
        let "counter=counter+1"
    elif [[ ${line: 0} != '"' && ${line: -1} == '"' ]];
    then
        to_combine[$counter]=$line
        joined=$(join_lines " " "${to_combine[@]}")
        #joined=$(join_lines " " "${to_combine[@]}" | tr -d "\n") # Mac sometimes introduces new lines, tr is used to remove newlines from joined.
        echo "$joined" >> tmp.csv
        unset to_combine
        let "counter=0"
    else
        echo "$line" >> tmp.csv
    fi
done < "$1"

while IFS= read -r line || [ -n "$line" ]; do
    if [[ ${line: 0} == '"' ]];
    then
        if [[ -f anomalies_$1 ]];
        then
            echo "${line}" >> anomalies_$1
        else
            touch anomalies_$1
            echo "${line}" >> anomalies_$1
        fi
    else
        echo "${line}" >> clean-data_$1
    fi
done < tmp.csv

rm -f tmp.csv

if [[ ( -f "anomalies.csv") && ($(tr -d '\n\r\t' < anomalies.csv | wc -c) -eq 0) ]]; 
then 
    anmls=$(wc -l anomalies_$1 | awk '{print $1}')
    echo "Anomalies found!!!!! ${anmls} lines of anomalies are recorded in anomalies_$1."
else
    input_data=$(wc -l $1 | awk '{print $1}')
    clean_lines=$(wc -l clean-data_$1 | awk '{print $1}')
    echo "${clean_lines} lines of clean data out of ${input_data} is recorded in clean-data_$1."
fi
