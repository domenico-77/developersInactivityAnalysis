#!/bin/bash

path=$1
currentpath=${PWD}
now=$(date)
echo -e \\n$now: BEGIN linguist script\\n 

ruby linguist.rb $currentpath/$path > $path/linguistfiles.log

echo -e "linguistfile.log was generated in $path folder:  \\n" 
now=$(date)
echo -e $now: END linguist script\\n
