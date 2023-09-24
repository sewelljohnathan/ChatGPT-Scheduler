#!/bin/bash
for input in ./tests/*.in; do
    output="${input%.*}.out"
    tmp=$(mktemp)
    cp "$output" "$tmp"
    
    ./scheduler-gpt.py "$input"
    diff "$output" "$tmp"

    cp "$tmp" "$output"
    rm "$tmp"
done