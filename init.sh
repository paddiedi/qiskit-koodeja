#!/usr/bin/env bash
python -m venv main
source main/bin/activate
pip install --upgrade pip setuptools wheel
pip install qiskit qiskit-aer qiskit-ibm-runtime matplotlib numpy scipy jupyter pylatexenc


