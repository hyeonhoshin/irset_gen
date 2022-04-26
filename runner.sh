#!/bin/bash

folder=$1
subject=$2
distance=$3
take=$4

python3 main.py ${folder} ${subject} ${distance} ${take} --count 200
