# Copyright (c) 2012-2013 ARM Limited
# All rights reserved.
#
# The license below extends only to copyright in the software and shall
# not be construed as granting a license to any other intellectual
# property including but not limited to intellectual property relating
# to a hardware implementation of the functionality of the software
# licensed hereunder.  You may use the software subject to the license
# terms below provided that you ensure that this notice is replicated
# unmodified and in its entirety in all distributions of the software,
# modified or unmodified, in source code or in binary form.
#
# Copyright (c) 2006-2008 The Regents of The University of Michigan
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Steve Reinhardt

# Simple test script
#
# "m5 test.py"

import optparse
import sys
import os

import m5
from m5.defines import buildEnv
from m5.objects import *
from m5.util import addToPath, fatal

addToPath('../common')
addToPath('../ruby')

import Options
import Ruby
import Simulation
#import CacheConfig
import MemConfig
from Caches import *
from cpu2000 import *
from new_cache import *


parser = optparse.OptionParser()
# parser = argparse.ArgumentParser()
parser.add_option('--enable_smt', action="store_true")
parser.add_option('--workload', type="string", default="hello")
parser.add_option('--workload2', type="string", default="hello")
parser.add_option('--maximum_insts', type="int", default="200000000")
parser.add_option('--fetch_policy', type="string", default="RoundRobin")

Options.addCommonOptions(parser)
Options.addSEOptions(parser)

if '--ruby' in sys.argv:
    Ruby.define_options(parser)

# options = parser.parse_args()
(options, args) = parser.parse_args()

if args:
    print "Error: script doesn't take any positional arguments"
    sys.exit(1)

# ***************************custom design*****************************
root = Root(full_system = False)
root.system = System()
root.system.mem_mode = 'timing'
root.system.mem_ranges = [AddrRange ('2048MB')]
root.system.mem_ctrl = DDR4_2400_x64()
root.system.mem_ctrl.range = root.system.mem_ranges[0]
root.system.cpu = DerivO3CPU()  # should be o3 for smt

# configure two-level cache design
root.system.cpu.icache = L1ICache()
root.system.cpu.dcache = L1DCache()
root.system.l2cache = L2Cache()

root.system.cpu.icache.size = options.l1i_size
root.system.cpu.dcache.size = options.l1d_size
root.system.l2cache.size = options.l2_size

root.system.membus = SystemXBar()
#root.system.cpu.icache_port = root.system.membus.slave
#root.system.cpu.dcache_port = root.system.membus.slave
root.system.cpu.icache.cpu_side = root.system.cpu.icache_port
root.system.cpu.dcache.cpu_side = root.system.cpu.dcache_port
root.system.l2bus = L2XBar()
root.system.cpu.icache.mem_side = root.system.l2bus.slave
root.system.cpu.dcache.mem_side = root.system.l2bus.slave
root.system.l2cache.cpu_side = root.system.l2bus.master
root.system.l2cache.mem_side = root.system.membus.slave

# set cache replacement policy
root.system.cpu.icache.tags = LRU()
root.system.cpu.dcache.tags = LRU()
root.system.l2cache.tags = LRU()

root.system.mem_ctrl.port = root.system.membus.master
root.system.cpu.createInterruptController()
root.system.system_port = root.system.membus.slave
# root.system.cpu.interrupt[0].pio = root.system.membus.master
# root.system.cpu.interrupt[0].int_master = root.system.membus.slave
# root.system.cpu.interrupt[0].int_slave = root.system.membus.master

# modify cpu clock domain
root.system.clk_domain = SrcClockDomain()
root.system.clk_domain.clock = '2GHz'
root.system.clk_domain.voltage_domain = VoltageDomain()
root.system.cpu_clk_domain = SrcClockDomain()
root.system.cpu_clk_domain.clock = '2GHz'
root.system.cpu_clk_domain.voltage_domain = VoltageDomain()
root.system.cpu.clk_domain = root.system.cpu_clk_domain


# get processes
process = LiveProcess()
if options.workload == '2mm':
    process.cmd = ['test_bench/2MM/2mm_base']
elif options.workload == 'bfs':
    process.cmd = ['test_bench/BFS/bfs', '-f', 'test_bench/BFS/USA-road-d.NY.gr']
elif options.workload == 'bzip':
    process.cmd = ['test_bench/bzip2/bzip2_base.amd64-m64-gcc42-nn','test_bench/bzip2/input.source', '280']
elif options.workload == 'mcf':
    process.cmd = ['test_bench/mcf/mcf_base.amd64-m64-gcc42-nn','test_bench/mcf/inp.in']
elif options.workload == 'hello':
    process.cmd = ['tests/test-progs/hello/bin/arm/linux/hello']
else:
    process.cmd = ['tests/test-progs/hello/bin/arm/linux/hello']

process2 = LiveProcess()
if options.workload2 == '2mm':
    process2.cmd = ['test_bench/2MM/2mm_base']
elif options.workload2 == 'bfs':
    process2.cmd = ['test_bench/BFS/bfs', '-f', 'test_bench/BFS/USA-road-d.NY.gr']
elif options.workload2 == 'bzip':
    process2.cmd = ['test_bench/bzip2/bzip2_base.amd64-m64-gcc42-nn','test_bench/bzip2/input.source', '280']
elif options.workload2 == 'mcf':
    process2.cmd = ['test_bench/mcf/mcf_base.amd64-m64-gcc42-nn','test_bench/mcf/inp.in']
elif options.workload2 == 'hello':
    process2.cmd = ['tests/test-progs/hello/bin/arm/linux/hello']
else:
    process2.cmd = ['tests/test-progs/hello/bin/arm/linux/hello']

# set process
# root.system.cpu.max_insts_any_thread = 20000

# root.system.cpu.max_insts_any_thread = 200000000 # 0.2 billion
root.system.cpu.max_insts_any_thread = options.maximum_insts

if options.enable_smt:
    root.system.cpu.workload = [process, process2]
    root.system.cpu.numThreads = 2
    
    # # note: LSQ, IQ, and ROB seem not to support Dynamic, but only Partitioned... I don't know why
    # # therefore, I just double the queue depth in SMT mode, which may be unfair though.
    # root.system.cpu.LQEntries = 64
    # root.system.cpu.SQEntries = 64
    # root.system.cpu.numIQEntries = 128
    root.system.cpu.numROBEntries = 384

else:
    root.system.cpu.workload = process
    root.system.cpu.numThreads = 1
    
# root.system.cpu.smtFetchPolicy = 'RoundRobin'
root.system.cpu.smtFetchPolicy = options.fetch_policy
# root.system.cpu.smtCommitPolicy = 'OldestReady'

print '\n\n'
# if numPhysFloatRegs is less then 159, then the program abort with one thread
isa_numFloatRegs = 160
root.system.cpu.numPhysFloatRegs = 256+isa_numFloatRegs # default: 256
# numintreg?
root.system.cpu.createThreads()

# simulate start
m5.instantiate()
exit_event = m5.simulate()
print('Existing @ tick', 'because', exit_event.getCause())

# Simulation.run(options, root, system, FutureClass)
