#!/usr/bin/env bash

APIURL='https://api.linode.com/v4'

# check for essential commands in our PATH
for cmd in curl python; do
	if ! command -v $cmd &> /dev/null; then
		echo >&2 "error: \"$cmd\" not found!"
		exit 1
	fi
done

usage() {
    echo "$0 [images|sizes|regions]"
    echo
    echo "images: prints a list of public images."
    echo "sizes: prints a collection of Linode Types, including pricing and specifications."
    echo "regions: prints the regions available for Linode services."
}

# list VM images
ls_images() {
    (curl -s ${APIURL}/images/ || return $?) | \
        python -m json.tool
    return $?
}

# list VM sizes 
ls_sizes() {
    (curl -s ${APIURL}/linode/types || return $?) | \
        python -m json.tool
    return $?
}

# list VM regions
ls_regions() {
    (curl -s curl ${APIURL}/regions || return $?) | \
        python -m json.tool
    return $?
}

if [[ "$1" == "images" ]]; then
    ls_images
    exit $?
elif [[ "$1" == "sizes" ]]; then
    ls_sizes
    exit $?
elif [[ "$1" == "regions" ]]; then
    ls_regions
    exit $?
else
    usage
    exit 1
fi
