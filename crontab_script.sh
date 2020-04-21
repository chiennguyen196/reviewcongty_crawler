root_path=`dirname "$0"`
log_file=logs/log_crontab-`date "+%Y-%m-%d"`.txt
(
    cd $root_path
    date >> $log_file
    bash ./update-latest.sh >> $log_file 2>&1
    echo "=======================" >> $log_file
)