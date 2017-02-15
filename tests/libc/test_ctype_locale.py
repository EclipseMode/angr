import nose
import os
import archinfo
import simuvex
import angr
import subprocess

import logging
l = logging.getLogger('simuvex.libc.ctype_locale')


FAKE_ADDR = 0x100000

ctype_b_loc = lambda state, arguments: simuvex.SimProcedures['libc.so.6']['__ctype_b_loc'](FAKE_ADDR, archinfo.arch_from_id('AMD64')).execute(state, arguments=arguments)
ctype_tolower_loc = lambda state, arguments: simuvex.SimProcedures['libc.so.6']['__ctype_tolower_loc'](FAKE_ADDR, archinfo.arch_from_id('AMD64')).execute(state, arguments=arguments)
ctype_toupper_loc = lambda state, arguments: simuvex.SimProcedures['libc.so.6']['__ctype_toupper_loc'](FAKE_ADDR, archinfo.arch_from_id('AMD64')).execute(state, arguments=arguments)

# Just load a binary so that we can do the initialization steps from
# libc_start_main
file_path = os.path.dirname(os.path.abspath(__file__))
t_path = os.path.join(file_path, 'bin/ctype_b_loc.run')
b = angr.Project(t_path)
p = b.factory.full_init_state()
pg = b.factory.path_group(p)

# Find main located at 0x400596 to let libc_start_main do its thing
main = pg.explore(find=0x400596)


def test_ctype_b_loc():
    '''
    test_ctype_locale.test_ctype_b_loc

    const unsigned short * * __ctype_b_loc (void);

    Description

    The __ctype_b_loc() function shall return a pointer into an array of
    characters in the current locale that contains characteristics for each
    character in the current character set. The array shall contain a total
    of 384 characters, and can be indexed with any signed or unsigned char
    (i.e. with an index value between -128 and 255). If the application is
    multithreaded, the array shall be local to the current thread.

    This interface is not in the source standard; it is only in the binary
    standard.
    '''

    state = main.found[0].state
    b_loc_array_ptr = ctype_b_loc(state, []).ret_expr
    table_ptr = state.memory.load(b_loc_array_ptr, state.arch.bits/8, endness=state.arch.memory_endness)

    result = ''
    for i in range(-128, 256):
        # Each entry is 2 bytes
        result += "%d->0x%x\n" % (i, state.se.any_int(state.memory.load(table_ptr + (i*2),
                                                                        2,
                                                                        endness=state.arch.memory_endness)))

    # Check output of compiled C program that uses ctype_b_loc()

    bin_path = os.path.join(file_path, 'bin/ctype_b_loc.run')
    output = subprocess.check_output(bin_path, shell=True)
    nose.tools.assert_equal(result, output)


def test_ctype_tolower_loc():
    '''
    test_ctype_locale.test_ctype_tolower_loc

    int32_t * * __ctype_tolower_loc(void);

    Description:
    The __ctype_tolower_loc() function shall return a pointer into an array of
    characters in the current locale that contains lower case equivalents for
    each character in the current character set. The array shall contain a total
    of 384 characters, and can be indexed with any signed or unsigned char (i.e.
    with an index value between -128 and 255). If the application is
    multithreaded, the array shall be local to the current thread.

    This interface is not in the source standard; it is only in the binary
    standard.

    Return Value:
    The __ctype_tolower_loc() function shall return a pointer to the array of
    characters to be used for the ctype() family of functions (see <ctype.h>).
    '''

    state = main.found[0].state
    tolower_loc_array_ptr = ctype_tolower_loc(state, []).ret_expr
    table_ptr = state.memory.load(tolower_loc_array_ptr, state.arch.bits/8, endness=state.arch.memory_endness)

    result = ''
    for i in range(-128, 256):
        result += "%d->0x%x\n" % (i, state.se.any_int(state.memory.load(table_ptr + i,
                                                                        1,
                                                                        endness=state.arch.memory_endness)))

    # Check output of compiled C program that uses ctype_tolower_loc()
    bin_path = os.path.join(file_path, 'bin/ctype_tolower_loc.run')
    output = subprocess.check_output(bin_path, shell=True)
    nose.tools.assert_equal(result, output)


def test_ctype_toupper_loc():
    '''
    test_ctype_locale.test_ctype_toupper_loc

    int32_t * * __ctype_toupper_loc(void);

    Description:
    The __ctype_toupper_loc() function shall return a pointer into an array of
    characters in the current locale that contains upper case equivalents for
    each character in the current character set. The array shall contain a total
    of 384 characters, and can be indexed with any signed or unsigned char (i.e.
    with an index value between -128 and 255). If the application is
    multithreaded, the array shall be local to the current thread.

    This interface is not in the source standard; it is only in the binary
    standard.

    Return Value:
    The __ctype_toupper_loc() function shall return a pointer to the array of
    characters to be used for the ctype() family of functions (see <ctype.h>).
    '''

    state = main.found[0].state
    toupper_loc_array_ptr = ctype_toupper_loc(state, []).ret_expr
    table_ptr = state.memory.load(toupper_loc_array_ptr, state.arch.bits/8, endness=state.arch.memory_endness)

    result = ''
    for i in range(-128, 256):
        result += "%d->0x%x\n" % (i, state.se.any_int(state.memory.load(table_ptr + i,
                                                                        1,
                                                                        endness=state.arch.memory_endness)))

    # Check output of compiled C program that uses ctype_toupper_loc()
    bin_path = os.path.join(file_path, 'bin/ctype_toupper_loc.run')
    output = subprocess.check_output(bin_path, shell=True)
    nose.tools.assert_equal(result, output)


if __name__ == '__main__':
    g = globals().copy()
    for func_name, func in g.iteritems():
        if func_name.startswith("test_") and hasattr(func, "__call__"):
            func()
