# crawl latest companies
# for each company:
#       crawl_all_reviews -> hanle_update_company

# exit when any command fails
set -e

. ./path.sh
. ./config.sh

# Make temp folder
TEMP_FOLDER=$(mktemp -d)

echo "[INFO] Getting recently updated companies"
scrapy crawl get-recently-updated-companies -o $TEMP_FOLDER/recently.jl -t 'jl' --nolog
echo "[INFO] Got `wc -l $TEMP_FOLDER/recently.jl` companies"

while IFS= read -r line
do
    if [ ! -z "$line" ]; then
        id=$(echo "$line" | jq '.id' -r)
        url=$(echo "$line" | jq '.url' -r)
        out_file=${TEMP_FOLDER}/${id}.jl
        echo "[INFO] Crawling reivews from $id at $url"
        scrapy crawl get-all-reviews -o $out_file -t 'jl' -a url=$url --nolog
        # remove duplicate if it has
        cat $out_file | awk '!x[$0]++' > ${out_file}-temp && mv ${out_file}-temp $out_file
        # check out_file is empty or not?
        if [[ ! -s $out_file ]]; then
            echo "[WARNING]: Crawl review from $url fail"
            continue
        fi
        echo "[INFO] Update company to database"
        python handle-update-company.py $out_file
    fi
  

done <<< `cat $TEMP_FOLDER/recently.jl | sort | uniq`


#Remove temp folder
rm -r $TEMP_FOLDER
