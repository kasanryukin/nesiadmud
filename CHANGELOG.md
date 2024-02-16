# NakedMud v4.0.1
Compiled and tested on Debian Linux
## BREAKING CHANGES:
Python 2.x support has been removed, the entire system was modified to use Cython and has been tested with 3.10+ 
### MODIFIED:
- SConstruct file was modified to include libm automatically, it is needed for compiling.
### FIXED
- Unicode support caused some garbage spew on copyover, added some error handling for UnicodeDecode errors in process_colour_hook
- GCC10 now defaults to -fno-common, made changes to /scripts/* to use extern instead of relying on a compat feature in the compiler.
