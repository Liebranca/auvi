# sort of a pyside for Zajec/ZJC_CommonTypes

# just a convenience thing -- and peace of mind
# use a familiar naming scheme as C when dancing with it through ctypes

# and since i use fixed size values in the C side of dsm, better be consistent
# pretty sure it'd still somehow work without this precaution...
# ... but i don't like to take chances with this shit

#   ---     ---     ---     ---     ---
# you know we could just dump this in ESPECTRO.__init__ right?
# yeah! but then I can't just from ZJC import *
# i mean, not without potentially fucking everything up, maan!

from ctypes import (

    Structure,

    POINTER   as star,
    c_void_p  as voidstar,
    c_char_p  as charstar,

    c_size_t  as size_t,

    c_int8    as schar,
    c_int16   as sshort,
    c_int32   as sint,
    c_int64   as slong,

    c_uint8   as uchar,
    c_uint16  as ushort,
    c_uint32  as uint,
    c_uint64  as ulong,

    c_float,

    byref,
    pointer,
    cast
    );

#   ---     ---     ---     ---     ---

def cstr (s): return bytes   (s, "utf-8");
def mcstr(s): return charstar(cstr(s)   );

#   ---     ---     ---     ---     ---
