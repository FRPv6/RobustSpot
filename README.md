# WARM

## data

The data is in data/, each *.csv file represent a case data.

For each file, the column "min" is timestamp of each leaf node, the column "value" means stalling viewers, the column "cnt" means total viewers.And the others mean attributes.

The case list label is in config/anomaly.yaml.

For example:

```yaml
- data: case1_0821_1741394221 # anomaly case name
  timestamp: 1566397800 # anomaly timestamp
  cause: {'bitrate':2000,'p2p':1} # the real cause of anomaly
```

## result

The output of program is in result/, which is also a *.csv file.

Each row contains the predict cause and corresponding case name.

## run

If you want to run your own case data.

First, write a case item in config/anomaly.yaml, which contains "data" and "timestamp",  which will be read by the program, and anomaly case information will be analyzed.

Then, 

```shell
python main.py
```

The result is in result/ directory.