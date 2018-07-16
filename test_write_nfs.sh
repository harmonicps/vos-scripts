#!/bin/bash

date=/bin/date

for (( ; ; ))
do
  $date >> test_file_$HOSTNAME
sleep .5s
done