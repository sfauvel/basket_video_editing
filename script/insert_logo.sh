#!/bin/bash

# Passer le répertoire d'un match et un fichier logo.
# Le script va insérer le logo dans chaque vidéo et les placer dans un répertoire `logo`.
# Si un fichier existe déjà, il ne sera pas écrasé.
# Attention: si une vidéo a été construite partiellement, il faudra la supprimer pour la reconstruire.

MATCH_FOLDER=$1
LOGO=$2

function usage() {
    echo "Usage: $0 <match_folder> <logo>"
    echo "  match_folder: répertoire racine du match"
    echo "  logo: fichier image à insérer"
}

if [ -z $MATCH_FOLDER ]; then usage; exit 1; fi
if [ -z $LOGO ]; then usage; exit 1; fi

OUTPUT_FOLDER=$MATCH_FOLDER/logo
mkdir -p $OUTPUT_FOLDER

for f in $(ls $MATCH_FOLDER/video/*.mp4); do
    INPUT=$f
    OUTPUT=$OUTPUT_FOLDER/$(basename $f)
    
    if [ ! -f $OUTPUT ]; then
    # Original: 197 349 280
    # size: 58 182 952 time:  0m38,969s
    # ffmpeg -i $INPUT -i $LOGO  -filter_complex "[0:v][1:v] overlay=5:5" -crf 23 -preset veryfast -pix_fmt yuv420p -c:a copy $OUTPUT
    
    # size: 38 549 725 time:  0m39,399s
    # ffmpeg -i $INPUT -i $LOGO  -filter_complex "[0:v][1:v] overlay=5:5" -crf 26 -preset veryfast -pix_fmt yuv420p -c:a copy $OUTPUT
    
    # size:53 751 863 time:3m29,320s
    # ffmpeg -i $INPUT -i $LOGO -c:v libx265 -filter_complex "[0:v][1:v] overlay=5:5" -crf 23     $OUTPUT

    # size: 40 670 166 time:3m5,640s 
    # ffmpeg -i $INPUT -i $LOGO -c:v libx265 -x265-params crf=25 -filter_complex "[0:v][1:v] overlay=5:5" $OUTPUT

    # size: 26 986 302 time: 2m41,313s
    # 28, and it should visually correspond to libx264 video at CRF 23, but result in about half the file size.
        ffmpeg -i $INPUT -i $LOGO -c:v libx265 -x265-params crf=28 -filter_complex "[0:v][1:v] overlay=5:5" -r 30 $OUTPUT
    fi
done    
