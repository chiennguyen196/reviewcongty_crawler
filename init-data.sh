# exit when any command fails
set -e

. ./path.sh

# Make temp folder
TEMP_FOLDER=$(mktemp -d)

MAX_PAGES=5

COMPANIES_JL=${TEMP_FOLDER}/companies.jl

scrapy crawl get-all-companies -a n_pages=${MAX_PAGES} -o $COMPANIES_JL -t "jl" 

while IFS= read -r line
do
    slug=$(echo "$line" | jq '.slug' -r)
    url=$(echo "$line" | jq '.url' -r)
    out_file=${TEMP_FOLDER}/${slug}.jl
    scrapy crawl get-all-reviews -o $out_file -t 'jl' -a url=$url
    python handle-update-company.py $out_file
done < "$COMPANIES_JL"

#Remove temp folder
rm -r $TEMP_FOLDER