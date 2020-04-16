# Reviewcongty crawler
This project crawl data from https://reviewcongty.com

## Installation
### Requirements

```shell
mongodb
python3
pip3
```

### Setup
```shell
sudo apt-get install jq
pip install -r requirements.txt
```
> Change config in `config.sh`

## Run

To crawl all at first time, run:
```shell
bash init-data.sh
```
To update latest updated company at home page, run:
```shell
bash update-latest.sh
```
