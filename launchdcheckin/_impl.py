# Copyright (c) Aaron Gallagher <_@habnab.it>
# See COPYING for details.

import os

import cffi


ffi = cffi.FFI()
ffi.cdef("""

typedef struct _launch_data *launch_data_t;

typedef enum {
    LAUNCH_DATA_DICTIONARY = 1,
    LAUNCH_DATA_ARRAY,
    LAUNCH_DATA_FD,
    LAUNCH_DATA_INTEGER,
    LAUNCH_DATA_REAL,
    LAUNCH_DATA_BOOL,
    LAUNCH_DATA_STRING,
    LAUNCH_DATA_OPAQUE,
    LAUNCH_DATA_ERRNO,
    LAUNCH_DATA_MACHPORT,
} launch_data_type_t;

launch_data_type_t launch_data_get_type(const launch_data_t);
launch_data_t launch_data_new_string(const char *);
launch_data_t launch_msg(const launch_data_t);

launch_data_t launch_data_dict_lookup(const launch_data_t, const char *);
size_t launch_data_dict_get_count(const launch_data_t);
void launch_data_dict_iterate(
    const launch_data_t,
    void (*)(const launch_data_t, const char *, void *), void *);
launch_data_t launch_data_array_get_index(const launch_data_t, size_t);
size_t launch_data_array_get_count(const launch_data_t);

int launch_data_get_fd(const launch_data_t);
/* mach_port_t launch_data_get_machport(const launch_data_t); */
long long launch_data_get_integer(const launch_data_t);
bool launch_data_get_bool(const launch_data_t);
double launch_data_get_real(const launch_data_t);
const char *launch_data_get_string(const launch_data_t);
void *launch_data_get_opaque(const launch_data_t);
size_t launch_data_get_opaque_size(const launch_data_t);
int launch_data_get_errno(const launch_data_t);

""")

C = ffi.verify("""

#include <launch.h>

""")


data_type_map = {
    C.LAUNCH_DATA_DICTIONARY: 'dict',
    C.LAUNCH_DATA_ARRAY: 'array',
    C.LAUNCH_DATA_FD: 'fd',
    C.LAUNCH_DATA_INTEGER: 'integer',
    C.LAUNCH_DATA_REAL: 'real',
    C.LAUNCH_DATA_BOOL: 'bool',
    C.LAUNCH_DATA_STRING: 'string',
    C.LAUNCH_DATA_OPAQUE: 'opaque',
    C.LAUNCH_DATA_ERRNO: 'errno',
    C.LAUNCH_DATA_MACHPORT: 'machport',
}


def _raise_from_errno():
    raise OSError(ffi.errno, os.strerror(ffi.errno))


class LaunchData(object):
    def __init__(self, data):
        self._data = data

    @classmethod
    def from_string(cls, string):
        data = C.launch_data_new_string(string)
        if not data:
            _raise_from_errno()
        return cls(data)

    def msg(self):
        data = C.launch_msg(self._data)
        if not data:
            _raise_from_errno()
        return type(self)(data)

    @property
    def type(self):
        return data_type_map[C.launch_data_get_type(self._data)]

    @property
    def data(self):
        typ = self.type
        method = getattr(self, '_data_' + typ, None)
        if method is None:
            method = getattr(C, 'launch_data_get_' + typ, None)
        if method is None:
            raise ValueError("can't get the data out of a %r" % (typ,))
        return method(self._data)

    def _data_string(self, data):
        return ffi.string(C.launch_data_get_string(data))

    def _data_opaque(self, data):
        return ffi.buffer(C.launch_data_get_opaque(data),
                          C.launch_data_get_opaque_size(data))[:]

    def __getitem__(self, item):
        typ = self.type
        if typ == 'dict':
            data = C.launch_data_dict_lookup(self._data, item)
            if not data:
                raise KeyError(item)
            return type(self)(data)
        elif typ == 'array':
            data = C.launch_data_array_get_index(self._data, item)
            if not data:
                raise IndexError(item)
            return type(self)(data)
        else:
            raise ValueError("can't index a %r" % (typ,))

    def __len__(self):
        typ = self.type
        method = getattr(C, 'launch_data_%s_get_count' % (typ,), None)
        if method is None:
            raise ValueError("can't get the length of a %r" % (typ,))
        return method(self._data)

    def as_dict(self):
        if self.type != 'dict':
            raise ValueError("can't get a dict from a %r" % (self.type,))

        result = {}

        @ffi.callback('void(const launch_data_t, const char *, void *)')
        def got_key(data, name, ign):
            result[ffi.string(name)] = type(self)(data)

        C.launch_data_dict_iterate(self._data, got_key, ffi.NULL)
        return result
