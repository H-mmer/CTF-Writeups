#!/bin/bash

a="ABCDEFGHIJKLMNOPQRSTUVWXYZ"

for y in {1..22}
do
s=`cat cipher.txt | cut -b $y | tr -d '\n'`
  for x in {0..25}
  do
      char=${a:$x:1}
      if [[ $s == *"$char"* ]]
      then
          printf ''
      else
          printf ${a:$x:1}
      fi
   done
done