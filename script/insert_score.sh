#!/bin/bash

# TODO: Add a fade apparition of score
# TODO: Display how many points are score (+1, +2, +3)
# https://stackoverflow.com/questions/50735335/ffmpeg-adding-text-to-a-video-between-two-times

MATCH_FOLDER=$1

function usage() {
    echo "Usage: $0 <match_folder>"
    echo "  match_folder: répertoire contenant les vidéos"
}

if [ -z $MATCH_FOLDER ]; then usage; exit 1; fi

INPUT_FOLDER=$MATCH_FOLDER/logo
ASS_FOLDER=$MATCH_FOLDER/ass
OUTPUT_FOLDER=$MATCH_FOLDER/output
mkdir -p $OUTPUT_FOLDER

for ASS_FILE in $(ls $ASS_FOLDER/*.ass); do
    FILENAME=$(basename ${ASS_FILE%.ass})
    INPUT=$INPUT_FOLDER/$(basename $FILENAME).mp4
    OUTPUT=$OUTPUT_FOLDER/$FILENAME.mp4
    ffmpeg -i $INPUT -vf "ass=$ASS_FILE" -c:a copy -c:v libx265 -crf 28 $OUTPUT
done