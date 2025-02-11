

path=$1
output=$2
temp="$output/tmp"

if [ -z "$path" ]; then
    echo "Usage: $0 <path> <output>"
    exit 1
fi

if [ -z "$output" ]; then
    echo "Usage: $0 <path> <output>"
    exit 1
fi
mkdir -p $output
mkdir -p $temp

for filepath in $path/*.mp4; do
    echo $filepath
    filename=$(basename $filepath)
    echo $filename

    name=${filename%.*}

    if [ -f $output/$name.csv ]; then
        echo "Csv file $name already exists"
    else
        echo "Processing $name"
        time unbuffer python3 run_detect.py $filepath > $temp/$name.txt
        python3 extract_frames.py $temp/$name.txt > $output/$name.csv
    fi
done
