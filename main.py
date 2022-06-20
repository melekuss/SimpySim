"""
Use of SimComponents to simulate the network of queues from Homework #6 problem 1, Fall 2014.
See corresponding solution set for mean delay calculation based on Burkes theorem.

Copyright 2014 Dr. Greg M. Bernstein
Released under the MIT license
"""
import random
import functools

import simpy

from SimComponents import PacketGenerator, PacketSink, SwitchPort, FlowDemux, PortMonitor, \
    SnoopSplitter, PacketGenerator2, RoundRobinQueue


def f(a):
    return a

if __name__ == '__main__':
    # Set up arrival and packet size distributions
    # Using Python functools to create callable functions for random variates with fixed parameters.
    # each call to these will produce a new random value.
    mean_pkt_size = 120.0  # in bytes
    adist1 = functools.partial(f, 1)
    adist2 = functools.partial(random.expovariate, 3.0)
    adist3 = functools.partial(random.expovariate, 2.0)
    sdist = functools.partial(f, mean_pkt_size)
    samp_dist = functools.partial(f, mean_pkt_size)
    port_rate = 7*8*mean_pkt_size  # want a rate of 2.2 packets per second

    # Create the SimPy environment. This is the thing that runs the simulation.
    env = simpy.Environment()

    # Create the packet generators and sink

    ps1 = PacketSink(env, debug=False, rec_arrivals=True)
    ps2 = PacketSink(env, debug=False, rec_arrivals=True)
    pg1 = PacketGenerator(env, "SJSU1", adist1, sdist, 0)
    pg2 = PacketGenerator2(env, "SJSU2", adist2, sdist, 1)
    pg3 = PacketGenerator2(env, "SJSU3", adist3, sdist, 2)
    snoop1 = SnoopSplitter()
    switch_port1 = RoundRobinQueue(env, port_rate)
    demux = FlowDemux()
    switch_port2 = RoundRobinQueue(env, port_rate)
    pm1 = PortMonitor(env,switch_port1,samp_dist)
    pm2 = PortMonitor(env,switch_port2,samp_dist)
    # Wire packet generators, switch ports, and sinks together
    pg1.out = switch_port1
    pg2.out = switch_port1
    switch_port1.out = snoop1
    snoop1.out1 = ps2
    snoop1.out2 = demux
    demux.outs = [switch_port2]
    pg3.out = switch_port2
    switch_port2.out = ps1


    # Run it
    env.run(until=4000)
    #print(switch_port1.store2.items)
    # print pm.sizes[-10:]
    print("average wait source 2 = {}".format(sum(ps1.waits)/len(ps1.waits)))
    print("average wait source 1 = {}".format(sum(ps2.waits) / len(ps2.waits)))
    print("packets received 2: {}".format(len(ps1.waits)))
    print("packets received 1: {}".format(len(ps2.waits)))
    print("average system occupancy1: {}".format(float(sum(pm1.sizes))/len(pm1.sizes)))
    print("average system occupancy2: {}".format(float(sum(pm2.sizes))/len(pm2.sizes)))