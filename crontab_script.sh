root_path=`dirname "$0"`
log_file=log_crontab.txt
(
    cd $root_path
    date >> $log_file
    bash ./update-latest.sh >> $log_file
    echo "=======================" >> $log_file
)