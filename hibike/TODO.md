# Thing to do for Hibike

## Protocol Updates (hibike/protocol2.0)

Design, document and implementat the next version of the hibike protocol. See README.md in the hibike/protocol2.0 branch.

### Tasks:

- Test actual usb-serial throughput
- Update protocol documentation
- Rewrite hibike_message.py
- Rewrite lib/hibike

## Python Rewrite / Concurrency (hibike/concurrency)

Rewrite hibike.py to implement concurrency more cleanly and efficiently.


### Tasks:

- Test having a read and write thread share a serial port
- Create runnable skeleton code

## Runtime-Hibike Integration / Simulation (hibike/atalanta)

Design a protocol for runtime-hibike communication over python multiprocessing Queues

Implement a runtime simulator that uses this protocol for testing.

### Tasks:

- Design and Document a provisional protocol; talk to runtime team
- Write a simulator for this protocol
