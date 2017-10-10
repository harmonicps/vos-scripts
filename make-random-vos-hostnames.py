#!/usr/bin/env python

import random

def post_random():

    n_choice = "abcdefghijklmnopqrstuvwxyz0123456789"

    p1 = ''.join((random.choice(n_choice)) for x in range(12))
    p2 = ''.join((random.choice(n_choice)) for x in range(12))

    return p1 + "-" + p2

host_prefix = raw_input("Enter Node Prefix: Ex: p1-ol-vos-node-fued36bvvkxt-\n")

n_nodes= raw_input("Node Number: ")


for n in range(int(n_nodes)):
    print host_prefix+ post_random()