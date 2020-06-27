#!/bin/bash

mkdir templates
echo create temp directory templates
cp main.html cosine.html word.html templates
echo copy files to templates directory
cd elasticsearch-7.6.2
./bin/elasticsearch -d
cd
python3 main.py
