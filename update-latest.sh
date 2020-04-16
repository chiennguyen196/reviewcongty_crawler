# crawl latest companies
# for each company:
#       crawl_all_reviews -> hanle_update_company

# exit when any command fails
set -e

. ./path.sh

# Make temp folder
TEMP_FOLDER=$(mktemp -d)

scrapy crawl get-recently-updated-companies -o $TEMP_FOLDER/recently.jl -t 'jl'

while IFS= read -r line
do
    if [ ! -z "$line" ]; then
        slug=$(echo "$line" | jq '.slug' -r)
        url=$(echo "$line" | jq '.url' -r)
        out_file=${TEMP_FOLDER}/${slug}.jl
        scrapy crawl get-all-reviews -o $out_file -t 'jl' -a url=$url
        python handle-update-company.py $out_file
    fi
  

done <<< `cat $TEMP_FOLDER/recently.jl | sort | uniq`


#Remove temp folder
rm -r $TEMP_FOLDER
