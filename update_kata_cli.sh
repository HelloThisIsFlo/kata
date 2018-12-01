#!/bin/bash

rm ~/.katacli
pip uninstall -y kata && python setup.py install
