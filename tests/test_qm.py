import time
import pytest
from quine_mccluskey_tomas789.qm import QuineMcCluskey


# generate_input
###############################################################################
def generate_input(s_terms):
    """
    generate input for a desired result
    """
    qm = QuineMcCluskey()
    res = set()
    if len(s_terms) == 0:
        return res
    for term in s_terms:
        res = res | set([i for i in qm.permutations(term)])
    return res


# format_set
###############################################################################
def format_set(s):
    """
    Format a set of strings.
    """
    max_el = 50
    if not s:
        return ""
    l = list(s)
    ret = "'" + "', '".join(l[:min(max_el, len(s))]) + "'"
    if len(s) > max_el:
        ret = ret + ", ..."
    return ret


# run function
###############################################################################
def run(test, use_xor):
    """
    Run function
    """
    qm = QuineMcCluskey(use_xor = use_xor)

    s_out = test['res']
    if 'ons' in test or 'dnc' in test:
        if 'ons' in test:
            ones = test['ons']
        else:
            ones = []

        if 'dnc' in test:
            dontcares = test['dnc']
        else:
            dontcares = []
        pretty_ones = "%s" % ones
        pretty_dontcares = "%s" % dontcares

        t1 = time.time()
        s_res = qm.simplify(ones, dontcares)
        t2 = time.time()
    else:
        s_ones = generate_input(s_out)
        s_dontcares = set()
        pretty_ones = "[%s]" % format_set(s_ones)
        pretty_dontcares = "[%s]" % format_set(s_dontcares)

        t1 = time.time()
        s_res = qm.simplify_los(s_ones, s_dontcares)
        t2 = time.time()


    print()
    print("ones:        %s" % pretty_ones)
    print("dontcares:   %s" % pretty_dontcares)
    print("res:         [%s]" % format_set(s_res))
    print('time:        %0.3f ms, %d comparisons, %d XOR and %d XNOR comparisons' % ((t2-t1)*1000.0, qm.profile_cmp, qm.profile_xor, qm.profile_xnor))
    assert s_res == s_out

common_test_vector = [
    { 'res': set(['----']), 'ons': [], 'dnc': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] },
    { 'res': set(['----']), 'ons': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] },
    { 'res': set(['----']), 'ons': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 'dnc': [10, 11, 12, 13, 14, 15] },
    { 'res': set(['----']), 'ons': [1, 3, 5, 7, 9, 11, 13, 15], 'dnc': [0, 2, 4, 6, 8, 10, 12, 14] },
]
noxor_test_vector = [
    { 'res': set(['010-', '1-01', '111-', '0-11']), 'ons': [3,4,5,7,9,13,14,15] },
]
xor_test_vector = [
    { 'res': set(['--^^']) },
    { 'res': set(['1--^^']) },
    { 'res': set(['-10']), 'ons': [2], 'dnc': [4, 5, 6, 7] },
    { 'res': set(['--1--11-', '00000001', '10001000']) },
    { 'res': set(['--^^']), 'ons': [1, 2, 5, 6, 9, 10, 13, 14] },
    { 'res': set(['^^^^']), 'ons': [1, 7, 8, 14], 'dnc': [2, 4, 5, 6, 9, 10, 11, 13] },
    { 'res': set(['-------1']) },
    { 'res': set(['------^^']) },
    { 'res': set(['-----^^^']) },
    { 'res': set(['0^^^']) },
    { 'res': set(['0~~~']) },
    { 'res': set(['^^^^^^^^']) },
    { 'res': set(['^^^0', '100-']) },
    { 'res': set(['00^-0^^0', '01000001', '10001000']) },
    { 'res': set(['^^^00', '111^^']) },
    { 'res': set(['---00000^^^^^^^']) },
]

@pytest.mark.parametrize("input", common_test_vector)
def test_common_with_xor(input):
    run(input, use_xor=True)


@pytest.mark.parametrize("input", common_test_vector)
def test_common_without_xor(input):
    run(input, use_xor=False)

@pytest.mark.parametrize("input", noxor_test_vector)
def test_noxor_without_xor(input):
    run(input, use_xor=False)

@pytest.mark.parametrize("input", xor_test_vector)
def test_xor_with_xor(input):
    run(input, use_xor=True)
