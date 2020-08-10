# WARM

## run

```sh
python main.py
```



## data

The data is in data/, each *.csv file represent a case data.

For each file, the column "min" is timestamp of each leaf node, the column "value" means stalling viewers, the column "cnt" means total viewers.And the others mean attributes.

## result

The output of program is in result/, which is also a *.csv file.

"predict_cause" is the final root cause of each case, "real_cause" is the label of each case.

"row", "col", "cost_time" are three Statistical indicators of program.

