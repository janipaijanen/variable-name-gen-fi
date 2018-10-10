This script generates dedupe-variable-name version 0.0.13 (https://pypi.org/project/dedupe-variable-name) compatible gender and frequency python contents, thats contents for files `frequency.py` and `gender.py`

This script uses data from Finnish Population Register Centre, see LICENSE.txt.

Given names and Surnames are from Finland.

Usage:
```bash
python make-dedupe.py -pg -pf \
-g source-data/etunimitilasto-2018-09-03-vrk.xlsx  \
-s source-data/sukunimitilasto-2018-09-03-vrk.xlsx
```
