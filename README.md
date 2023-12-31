# SingleScan: A Comprehensive Single Cell Analysis Database
SingleScan is a manually curated resource for single-cell transcriptome/genome analysis pipeline and usage scenarios. At present, >1500 tools and 300 publications have been integrated in this resource. SingleScan enables users to quickly explore the features of each tool and role of the tool in the entire data analysis procedure. Meanwhile, SingleScan builds a benchmark pool that collects the published benchmark articles that it produces the best practices recommendations for approaching a standard analysis. Thus, it facilitates users to select and integrate appropriate tools into their own data processing pipelines.

# Online Database
SingleScan database is publicly accessible via the website at http://cailab.labshare.cn/SingleScan or http://cailab.labshare.cn:7003/

## Installation:
```Bash
pip install -r requirements.txt
```
## Quick Start
```Bash
PROXY = 'your proxy' # make sure you input the correct proxy in googlescholar2.py

python googlescholar2.py doi.txt out.csv
```
## Check Results
>If the result is incomplete, it may be due to the network, run it a few more times to get the complete result.<br/>
>Or check if your proxy is working
