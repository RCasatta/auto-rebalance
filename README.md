# auto-rebalance

`auto-rebalance.py` is a script for [c-lighting](https://github.com/ElementsProject/lightning) that automatically calls the [rebalance](https://github.com/lightningd/plugins/tree/master/rebalance) plugin trying to keep channels at about 50% of capacity.

This is done to increase the chance of success in routing and being able to send and receive without capacity issues. To avoid loosing money in the process, the rebalance is attempted only if the fee rate requested is lower than the node fee rate.

The script is kept running indefinitely and try to rebalance every 12 hours by default.

## Launch:

`LIGHTNING_RPC=/home/user/.lighthing/bitcoin/lightnig-rpc ./auto-rebalance.py`

Since the script runs indefinetely you may want to run it in a `screen` or `tmux` session

## Example output

```
fee_base=1000 fee_per_satoshi=1000 maxfeepercent=0.10
skipping {'to_us': 889648052msat, 'to_them': 1070351948msat, 'chan_id': 'XXX', 'to_middle': 90351948msat, 'percent': 4}
skipping {'to_us': 7445916685msat, 'to_them': 8995753315msat, 'chan_id': 'XXX', 'to_middle': 774918315msat, 'percent': 4}
skipping {'to_us': 520851157msat, 'to_them': 459148843msat, 'chan_id': 'XXX', 'to_middle': 30851157msat, 'percent': 3}
skipping {'to_us': 371365596msat, 'to_them': 364614404msat, 'chan_id': 'XXX', 'to_middle': 3375596msat, 'percent': 0}
skipping {'to_us': 8602547140msat, 'to_them': 7839123860msat, 'chan_id': 'XXX', 'to_middle': 381711640msat, 'percent': 2}
skipping {'to_us': 5000068436msat, 'to_them': 4799931564msat, 'chan_id': 'XXX', 'to_middle': 100068436msat, 'percent': 1}
skipping {'to_us': 980563184msat, 'to_them': 849854816msat, 'chan_id': 'XXX', 'to_middle': 65354184msat, 'percent': 3}
skipping {'to_us': 2402264678msat, 'to_them': 1986023322msat, 'chan_id': 'XXX', 'to_middle': 208120678msat, 'percent': 4}
skipping {'to_us': 223598000msat, 'to_them': 266402000msat, 'chan_id': 'XXX', 'to_middle': 21402000msat, 'percent': 4}
skipping {'to_us': 118194045msat, 'to_them': 111671955msat, 'chan_id': 'XXX', 'to_middle': 3261045msat, 'percent': 1}
skipping {'to_us': 308614000msat, 'to_them': 356072000msat, 'chan_id': 'XXX', 'to_middle': 23729000msat, 'percent': 3}
skipping {'to_us': 84681000msat, 'to_them': 99309000msat, 'chan_id': 'XXX', 'to_middle': 7314000msat, 'percent': 3}
skipping {'to_us': 288241000msat, 'to_them': 299759000msat, 'chan_id': 'XXX', 'to_middle': 5759000msat, 'percent': 0}

incoming
{'to_us': 38416000msat, 'to_them': 79184000msat, 'chan_id': 'XXX', 'to_middle': 20384000msat, 'percent': 17}
{'to_us': 83608063msat, 'to_them': 406391937msat, 'chan_id': 'XXX', 'to_middle': 161391937msat, 'percent': 32}
{'to_us': 485594689msat, 'to_them': 3838102311msat, 'chan_id': 'XXX', 'to_middle': 1676253811msat, 'percent': 38}

outgoing
{'to_us': 218051941msat, 'to_them': 146649059msat, 'chan_id': 'XXX', 'to_middle': 35701441msat, 'percent': 9}
{'to_us': 2086037519msat, 'to_them': 13837481msat, 'chan_id': 'XXX', 'to_middle': 1036100019msat, 'percent': 49}
{'to_us': 2216932000msat, 'to_them': 0msat, 'chan_id': 'XXX', 'to_middle': 1108466000msat, 'percent': 50}
{'to_us': 3100140062msat, 'to_them': 77986938msat, 'chan_id': 'XXX', 'to_middle': 1511076562msat, 'percent': 47}
{'to_us': 4828528902msat, 'to_them': 699574098msat, 'chan_id': 'XXX', 'to_middle': 2064477402msat, 'percent': 37}

skipping ['XXX', 'XXX', 'XXX'] because channels failed more than 2 times
skipping ['XXX', 'XXX'] because channels failed more than 2 times
total_out_success Counter({'XXX': 1, 'XXX': 0, 'XXX': -2, 'XXX': -3, 'XXX': -3})
total_inc_success Counter({'XXX': 2, 'XXX': -3, 'XXX': -3, 'XXX': -3})
resetting counters
there are no incoming or outgoing channel to rebalance, sleeping for 43200s
```

The `total_inc_success` and `total_out_success` are updated through runs and are useful to see problematic channels that fails every time.