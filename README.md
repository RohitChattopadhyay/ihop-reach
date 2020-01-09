# PUBMED Extraction

This branch handles extraction of required journals from PUBMED FTP. Further processing of the files is done using branch [docker/pipeline/ftp-processor](https://github.com/cannin/ihop-reach/tree/docker/pipeline/ftp-processor).

### Components
There are mainly following two components:
1. *`interesting_table`* generates table of journals which we are interested in.
	**Instructions to run**
	```
	1. cd interesting_table
	2. pipenv install
	3. python script.py
	```
	**`	interesting_journals_table_output.csv`** will have the desired table. 
2. *`extraction`* downloads archive files from [PUBMED FTP](ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/) and extracts the desired journals.
	**Instructions to run**
	```
	1. cd extraction
	2. pipenv install
	3. python extraction.py -p .<PATH TO interesting_journals_table_output.csv>
	Usage: extraction.py [-h] [--path PATH]
	optional arguments:
	  -h, --help            Show this help message and exit
	  --path PATH, -p PATH  Path to list of journals
	  ```
	  Extracted journals will be in folder named **`papers`**, content of this directory is to be passed to [REACH-Processor](https://github.com/cannin/ihop-reach/tree/docker/pipeline/ftp-processor).
