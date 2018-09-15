#!/bin/bash

USER=FlorianKempenich
REPO=ansible-role-python-virtualenv
URL=https://api.github.com/repos/$USER/$REPO/contents

FILE_PATH="$1"

curl -s $URL/$FILE_PATH | jq '.[] | {name, path, type, download_url}'
