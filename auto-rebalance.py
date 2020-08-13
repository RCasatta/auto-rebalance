#!/usr/bin/env python3

"""
Try rebalance if lower than our fee
"""

from pyln.client import LightningRpc, Millisatoshi
from collections import Counter
import random
import time
import os

SLEEP_BETWEEN_ATTEMPTS = 10
SLEEP_WHEN_NO_UNBALANCED = 12 * 60 * 60
SKIPPING_PERC = 5
MAX_FAILING = 2


def print_list(l):
    for el in l:
        print(el)
    print()


def channels_to_rebalance(rpc):
    incoming = []
    outgoing = []
    peers = rpc.listpeers()
    for p in peers['peers']:
        if not p['connected']:
            continue
        for c in p['channels']: 
            if c['state'] != 'CHANNELD_NORMAL':
                continue
            if c['short_channel_id'] in exclude:
                continue
            if c['our_reserve_msat'] < c['to_us_msat']:
                to_us = c['to_us_msat'] - c['our_reserve_msat']
            else:
                to_us = Millisatoshi(0)

            to_them = c['total_msat'] - c['to_us_msat']
            if c['their_reserve_msat'] < to_them:
                to_them = to_them - c['their_reserve_msat']
            else:
                to_them = Millisatoshi(0)

            middle = (to_us + to_them)/2
            to_middle = to_us - middle if to_us > to_them else to_them - middle
            perc = int((to_middle.to_satoshi() / (to_us+to_them).to_satoshi())*100)

            chan = { 'to_us': to_us, 'to_them': to_them, 'chan_id': c['short_channel_id'], 'to_middle': to_middle, 'percent': perc }
            if perc < SKIPPING_PERC:  # consider balanced channel around 10% from middle
                print("skipping %s" % str(chan))
                continue
            if to_us > to_them:
                outgoing.append(chan)
            else:
                incoming.append(chan)

    incoming = sorted(incoming, key=lambda k: k['to_middle'])
    outgoing = sorted(outgoing, key=lambda k: k['to_middle'])

    print()
    print("incoming")
    print_list(incoming)
    print("outgoing")
    print_list(outgoing)

    return incoming, outgoing


if __name__ == "__main__":
    rpc = LightningRpc(os.environ['LIGHTNING_RPC'])
    out_success = Counter()
    inc_success = Counter()
    total_out_success = Counter()
    total_inc_success = Counter()
    exclude = []

    while True:
        print("----------------------------------")
        config = rpc.listconfigs()
        fee_base = config['fee-base']
        fee_per_satoshi = config['fee-per-satoshi']  # microsat per sat
        maxfeepercent = fee_per_satoshi * 0.000001 * 100  # my fee in percent
        print("fee_base=%d fee_per_satoshi=%d maxfeepercent=%.2f" % (fee_base, fee_per_satoshi, maxfeepercent) )
        
        (incoming, outgoing) = channels_to_rebalance(rpc)

        if inc_success and incoming:
            old_incoming = list(incoming)
            to_skip = list(filter(lambda x: inc_success[x] < -MAX_FAILING, inc_success))
            incoming = list(filter(lambda x: x['chan_id'] not in to_skip, old_incoming))
            if old_incoming != incoming:
                print("skipping %s because channels failed more than %d times" % (str(to_skip), MAX_FAILING))
        if out_success and outgoing:
            old_outgoing = list(outgoing)
            to_skip = list(filter(lambda x: out_success[x] < -MAX_FAILING, out_success))
            outgoing = list(filter(lambda x: x['chan_id'] not in to_skip, old_outgoing))
            if old_outgoing != outgoing:
                print("skipping %s because channels failed more than %d times" % (str(to_skip), MAX_FAILING))

        if not incoming or not outgoing:
            total_out_success.update(out_success)
            total_inc_success.update(inc_success)
            out_success = Counter()
            inc_success = Counter()
            print("total_out_success " + str(total_out_success))
            print("total_inc_success " + str(total_inc_success))
            print("resetting counters")
            print("there are no incoming or outgoing channel to rebalance, sleeping for %ds" % SLEEP_WHEN_NO_UNBALANCED)
            time.sleep(SLEEP_WHEN_NO_UNBALANCED)
            continue

        inc_chan = random.choice(incoming)
        out_chan = random.choice(outgoing)

        max_val = int(min(inc_chan['to_middle'].to_satoshi(), out_chan['to_middle'].to_satoshi()) )
        min_val = 1000
        val = Millisatoshi(random.randint(min_val,max_val)*1000)

        params = dict( 
                outgoing_scid=out_chan['chan_id'], 
                incoming_scid=inc_chan['chan_id'], 
                msatoshi=val, 
                maxfeepercent=maxfeepercent, 
                retry_for=30,
                exemptfee=0
                )
        print(params)
        try:
            res = rpc.rebalance(**params)
            print("SUCCESS")
            print(res)
            out_success[out_chan['chan_id']] += 1
            inc_success[inc_chan['chan_id']] += 1
        except Exception as e:
            print("FAILURE")
            print(e)
            out_success[out_chan['chan_id']] -= 1
            inc_success[inc_chan['chan_id']] -= 1
        print("out_success " + str(out_success))
        print("inc_success " + str(inc_success))

        print("sleeping for %d" % SLEEP_BETWEEN_ATTEMPTS)
        time.sleep(SLEEP_BETWEEN_ATTEMPTS)
