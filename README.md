This is a mud server written in C with Python 3+. 

It is a derivative of NakedMud 3.8.1 written by Geoff Hollis. Please see CREDITS and doc/README for details. NakedMud was left in a very workable state with some bugs and some design decisions that needed to be dressed up and this is considered a continuation on that line. The goal is to continue the work of removing existing bugs while continuing the common-sense segregation of some of the core 'world' functionality. I will try to keep a full set of backwards compatibility where possible, while providing easy routes of migration where not.

Unfortunately moving to Python 3 will break a lot of lib/* compatibility for older modules.
