---
layout: default
title: OS
permalink: /learning-cs/os/
---
# Operating Systems

Notes on core operating system concepts.

## What an OS Does

An operating system manages hardware resources (CPU, memory, disk, I/O devices) and provides a stable, convenient interface for programs to run on top of. Its core jobs are:

- **Process management** — deciding what runs, when, and for how long
- **Memory management** — allocating and protecting memory between programs
- **File systems** — organizing persistent storage
- **I/O handling** — talking to devices through drivers
- **Security/isolation** — keeping processes from interfering with each other

## Processes vs. Threads

A **process** is a running program: its own address space, open file handles, and at least one thread of execution. A **thread** is a unit of execution within a process — threads in the same process share memory (heap, globals) but each has its own stack and registers.

| | Process | Thread |
|---|---|---|
| Memory | Isolated address space | Shared within process |
| Creation cost | Expensive | Cheap |
| Communication | IPC (pipes, sockets, shared memory) | Direct (shared variables) |
| Crash impact | Isolated to that process | Can crash the whole process |

## Scheduling

The scheduler decides which process/thread gets the CPU next. Common approaches:

- **FCFS (First-Come, First-Served)** — simple, but can cause long waits (convoy effect)
- **Round Robin** — each process gets a fixed time slice, then goes to the back of the queue; good for responsiveness
- **Priority Scheduling** — higher-priority tasks run first; risks starvation of low-priority tasks unless aging is used
- **Multilevel Feedback Queue** — combines multiple queues with different priorities/time slices, adapting to a process's behavior over time (used by most modern general-purpose OSes)

## Memory Management

- **Virtual memory**: each process sees its own contiguous address space, translated to physical memory (or disk) by the MMU using page tables. This gives isolation and lets total virtual memory exceed physical RAM.
- **Paging**: memory is split into fixed-size pages; a page fault occurs when a page needed isn't in physical memory and must be loaded (possibly evicting another page).
- **Segmentation**: divides memory into logical segments (code, stack, heap) — largely superseded by paging in modern systems but still conceptually present.

## Concurrency & Synchronization

Running multiple threads safely requires coordinating access to shared data:

- **Race condition** — outcome depends on timing of concurrent access to shared state
- **Mutex/lock** — ensures only one thread accesses a critical section at a time
- **Semaphore** — a counter-based primitive for controlling access to a limited number of resources
- **Deadlock** — two or more threads waiting on each other's locks forever; classic prevention is to always acquire locks in the same global order

## File Systems

A file system organizes how data is stored and retrieved from disk:

- Tracks free vs. used space
- Maps filenames/paths to physical blocks (via inodes, FAT tables, etc.)
- Provides metadata: permissions, timestamps, ownership
- Journaling file systems (ext4, NTFS) log changes before applying them, so a crash mid-write doesn't corrupt the whole filesystem

## Further Reading

- *Operating Systems: Three Easy Pieces* (free online) — great practical intro
- *Modern Operating Systems* by Tanenbaum — more textbook-style depth
