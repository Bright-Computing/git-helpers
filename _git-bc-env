#!/bin/sh

die () {
    die_with_status 1 $1
}

die_with_status () {
    STATUS=$1
    shift
    echo "$*"
    exit "$STATUS"
}

usage() {
    echo "$USAGE"
    exit 1
}

HELP=0
