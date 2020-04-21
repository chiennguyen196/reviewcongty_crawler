# exit when any command fails
set -e

. ./path.sh
. ./config.sh

# Make temp folder
TEMP_FOLDER=$(mktemp -d)

COMPANIES_JL=${TEMP_FOLDER}/companies.jl

# MAX_PAGE get from config.sh
echo "[INFO] Getting all companies from $START_PAGE to $MAX_PAGES"
scrapy crawl get-all-companies -a n_pages=${MAX_PAGES} -a start_page=${START_PAGE} -o $COMPANIES_JL -t "jl" --nolog
echo "[INFO] Got `cat $COMPANIES_JL | wc -l` companies"

while IFS= read -r line
do
    id=$(echo "$line" | jq '.id' -r)
    url=$(echo "$line" | jq '.url' -r)
    out_file=${TEMP_FOLDER}/${id}.jl
    echo "[INFO] Crawling reivews from $id at $url"
    scrapy crawl get-all-reviews -o $out_file -t 'jl' -a url=$url --nolog
    # check out_file is empty or not?
    if [[ ! -s $out_file ]]; then
        echo "[WARNING]: Crawl review from $url fail"
        continue
    fi
    echo "[INFO] Update company to database"
    python handle-update-company.py $out_file
done < "$COMPANIES_JL"

#Remove temp folder
# rm -r $TEMP_FOLDER