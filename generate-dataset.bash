#!/bin/bash
set -eu

IAMSURE=0
TRAINDEFAULT=1
TESTDEFAULT=1

TRAINDATA="$TRAINDEFAULT"
TESTDATA="$TESTDEFAULT"

intregex='^[1-9][0-9]*$'
checkint() {
    if [[ ! $1 =~ $intregex ]]; then
        echo "error: $1 is invalid"; exit 1
    fi
}

helper () {
    echo "generate-dataset.bash"
    echo ""
    echo "Generate training and test data for flatland"
    echo "creates folders called train/ and test/ in the current directory"
    echo ""
    echo "Syntax:"
    echo "generate-dataset.bash -N 20 -k 5"
    echo ""
    echo "  -N        number of training samples per subdomain"
    echo "  -k        number of test samples per subdomain"
    echo "  -y        skip confirmation to generate data"
    echo "  -h        show this help"
}

sample () {
    echo "testing that flatland-sample works...."
    echo ""
    flatland-sample
}

paramcheck() {
    echo "checking params..."
    checkint "$TRAINDATA"
    checkint "$TESTDATA"
}

rusure () {
    echo "This script is about to delete the train and test folders"
    TRAINTOTAL=$(( 10*$TRAINDATA ))
    TESTTOTAL=$(( (5+4+4)*$TESTDATA ))
    echo "and generate $TRAINTOTAL training samples, $TESTTOTAL testing samples."
    read -p "Press y to confirm. " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[^Yy]$ ]]
    then
        echo "Exiting."
        exit 1
    fi
}

maketrain () {
    echo "creating train folder..."
    mkdir -p ./train
    echo "generating training data...."
    flatland-generate -d circles -N 1 -n "$TRAINDATA" -x -o ./train
    flatland-generate -d circles -N 2 -n "$TRAINDATA" -x -o ./train
    flatland-generate -d circles -N 3 -n "$TRAINDATA" -x -o ./train
    flatland-generate -d circles -N 4 -n "$TRAINDATA" -x -o ./train
    flatland-generate -d circles -N 5 -n "$TRAINDATA" -x -o ./train
    flatland-generate -d lines -N 1 -n "$TRAINDATA" -x -o ./train
    flatland-generate -d lines -N 2 -n "$TRAINDATA" -x -o ./train
    flatland-generate -d lines -N 3 -n "$TRAINDATA" -x -o ./train
    flatland-generate -d lines -N 4 -n "$TRAINDATA" -x -o ./train
    flatland-generate -d lines -N 5 -n "$TRAINDATA" -x -o ./train
    echo ""
}

maketesteasy() {
    echo "creating test/easy folder..."
    mkdir -p "./test/easy"
    echo "generating testing data...."
    flatland-generate -d circles -N 1 -n "$TESTDATA" -x -o ./test/easy
    flatland-generate -d lines -N 1 -n "$TESTDATA" -x -o ./test/easy
    flatland-generate -d circles -N 2 -n "$TESTDATA" -x -o ./test/easy
    flatland-generate -d lines -N 2 -n "$TESTDATA" -x -o ./test/easy
    flatland-generate -d circles -N 3 -n "$TESTDATA" -x -o ./test/easy
    echo ""
}

maketestmedi() {
    echo "creating test/medium folder..."
    mkdir -p "./test/medium"
    echo "generating testing data...."
    flatland-generate -d circles -N 5 -n "$TESTDATA" -x -o ./test/medium
    flatland-generate -d lines -N 4 -n "$TESTDATA" -x -o ./test/medium
    flatland-generate -d rectangles -N 1 -n "$TESTDATA" -x -o ./test/medium
    flatland-generate -d circle_in_box -N 1 -n "$TESTDATA" -x -o ./test/medium
    echo ""
}

maketesthard() {
    echo "creating test/hard folder..."
    mkdir -p "./test/hard"
    echo "generating testing data...."
    flatland-generate -d rectangles -N 2 -n "$TESTDATA" -x -o ./test/hard
    flatland-generate -d circle_in_box -N 2 -n "$TESTDATA" -x -o ./test/hard
    flatland-generate -d rotline1 -n "$TESTDATA" -x -o ./test/hard
    flatland-generate -d stickfigure1 -N 1 -n "$TESTDATA" -x -o ./test/hard
    echo ""
}

generate () {
    echo "setting training samples as $TRAINDEFAULT"
    echo "setting test samples as $TESTDEFAULT"
    if [ "$IAMSURE" != "1" ]; then
        rusure
    fi
    paramcheck
    sample
    echo "removing existing train and test data..."
    rm -rf  "./train" "./test"
    echo ""
    maketrain
    maketesteasy
    maketestmedi
    maketesthard
    echo "DONE."
}

while getopts "N:k:hy" opt
do
    case "$opt" in
        h)  
            helper; exit 0   ;;
        N)
            TRAINDATA="$OPTARG";;
        k)
            TESTDATA="$OPTARG";;
        y)
            IAMSURE=1;;
        \?)  
            echo -e "\n  Option does not exist : $OPTARG\n"
            helper; exit 1   ;;
    esac
done

generate
