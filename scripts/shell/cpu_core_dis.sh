#!/bin/bash

TOTAL_CPU=$(nproc --all)
echo
echo "Total CPU(s):" $TOTAL_CPU

#Enable cores and Hiding unnecessary output to print on console menu
    max=$(lscpu  | grep CPU\(s\) | head -n 1 | cut -d':' -f2 | rev)
    dis="$(( $max -1))"
    { for CPU in /sys/devices/system/cpu/cpu[$1-$dis]*; do
        CPUID=$(basename $CPU)
        #echo "CPU: $CPUID";
        COREID="$(cat $CPU/topology/core_id)";
        eval "COREENABLE=\"\${core${COREID}enable}\"";
        #echo "$CPU core=${CORE} -> disable";
        echo "1" > "$CPU/online";
    done; } &> /dev/null
#Disabling the cpu cores with the user input

if [ "$1" -gt "1" -a "$1" -lt "$max" ]; then
	max=$(lscpu  | grep CPU\(s\) | head -n 1 | cut -d':' -f2 | rev)
	dis="$(( $max -1))"
    for CPU in /sys/devices/system/cpu/cpu[$1-$dis]*; do
        CPUID=$(basename $CPU)
        echo "CPU: $CPUID";
	echo "Disabling this core..."
        COREID="$(cat $CPU/topology/core_id)";
        eval "COREENABLE=\"\${core${COREID}enable}\"";
        echo "$CPU core=${CORE} -> disable";
	echo
        echo "0" > "$CPU/online";
    done;
	tc="$(( $1 - 1 ))"
	echo "Cores successfully disabled. On-line CPU(s) are: [0-$tc]"
	sleep 1
elif [ "$1" -eq "1" ]; then
	echo
	echo "Resetting..."
	TOTAL_CPU=$(nproc --all)
	ONLINE=$(nproc)
	sleep 1
	echo
	echo "Online CPU(s):" $ONLINE
	echo
else
	echo "This input parameter is NOT VALID!"
fi
