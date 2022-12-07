"""An implementation of the Quine McCluskey algorithm.

This implementation of the Quine McCluskey algorithm has no inherent limits
(other than the calculation time) on the size of the inputs.

Also, in the limited tests of the author of this module, this implementation is
considerably faster than other public Python implementations for non-trivial
inputs.

Another unique feature of this implementation is the possibility to use the XOR
and XNOR operators, in addition to the normal AND operator, to minimise the
terms. This slows down the algorithm, but in some cases it can be a big win in
terms of complexity of the output.
"""

from __future__ import print_function, annotations

import itertools
import math
import re
from typing import Dict, Iterable, List, Optional, Set, Tuple


class ResultWithProfile:
    """A wrapper around minimization results with profiling stats."""

    none: ResultWithProfile

    def __init__(self, result: Optional[Set[str]], profile_cmp: int, profile_xor: int, profile_xnor: int):
        self.result = result
        self.profile_cmp = profile_cmp
        self.profile_xor = profile_xor
        self.profile_xnor = profile_xnor


ResultWithProfile.none = ResultWithProfile(result=None, profile_cmp=0, profile_xor=0, profile_xnor=0)


def num2str(n_bits: int, i: int) -> str:
    """
    Convert an integer to its bit-representation in a string.

    Args:
        i (int): the number to convert.

    Returns:
        The binary string representation of the parameter i.
    """
    x = ["1" if i & (1 << k) else "0" for k in range(n_bits - 1, -1, -1)]
    return "".join(x)


def reduce_simple_xor_terms(t1: str, t2: str) -> Optional[str]:
    """Try to reduce two terms t1 and t2, by combining them as XOR terms.

    Args:
        t1 (str): a term.
        t2 (str): a term.

    Returns:
        The reduced term or None if the terms cannot be reduced.
    """
    assert len(t1) == len(t2)
    difft10: int = 0
    difft20: int = 0
    ret: List[str] = []
    for (t1c, t2c) in zip(t1, t2):
        if t1c == "^" or t2c == "^" or t1c == "~" or t2c == "~":
            return None
        if t1c != t2c:
            ret.append("^")
            if t2c == "0":
                difft10 += 1
            else:
                difft20 += 1
        else:
            ret.append(t1c)
    if difft10 == 1 and difft20 == 1:
        return "".join(ret)
    return None


def reduce_simple_xnor_terms(t1: str, t2: str) -> Optional[str]:
    """Try to reduce two terms t1 and t2, by combining them as XNOR terms.

    Args:
        t1 (str): a term.
        t2 (str): a term.

    Returns:
        The reduced term or None if the terms cannot be reduced.
    """
    difft10 = 0
    difft20 = 0
    ret = []
    for (t1c, t2c) in zip(t1, t2):
        if t1c == "^" or t2c == "^" or t1c == "~" or t2c == "~":
            return None
        if t1c != t2c:
            ret.append("~")
            if t1c == "0":
                difft10 += 1
            else:
                difft20 += 1
        else:
            ret.append(t1c)
    if (difft10 == 2 and difft20 == 0) or (difft10 == 0 and difft20 == 2):
        return "".join(ret)
    return None


def get_prime_implicants(n_bits: int, use_xor: bool, terms: Set[str]) -> ResultWithProfile:
    """Simplify the set 'terms'.

    Args:
        terms (set of str): set of strings representing the minterms of
        ones and dontcares.

    Returns:
        A set of prime implicants. These are the minterms that cannot be
        reduced with step 1 of the Quine McCluskey method.

    This is the very first step in the Quine McCluskey algorithm. This
    generates all prime implicants, whether they are redundant or not.
    """
    profile_cmp = 0
    profile_xor = 0
    profile_xnor = 0

    # Sort and remove duplicates.
    n_groups = n_bits + 1
    marked = set()

    # Group terms into the list groups.
    # groups is a list of length n_groups.
    # Each element of groups is a set of terms with the same number
    # of ones.  In other words, each term contained in the set
    # groups[i] contains exactly i ones.
    groups_1: List[Set[str]] = [set() for i in range(n_groups)]
    for t in terms:
        n_bits = t.count("1")
        groups_1[n_bits].add(t)
    if use_xor:
        # Add 'simple' XOR and XNOR terms to the set of terms.
        # Simple means the terms can be obtained by combining just two
        # bits.
        for gi, group in enumerate(groups_1):
            for t1 in group:
                for t2 in group:
                    t12 = reduce_simple_xor_terms(t1, t2)
                    if t12 is not None:
                        terms.add(t12)
                if gi < n_groups - 2:
                    for t2 in groups_1[gi + 2]:
                        t12 = reduce_simple_xnor_terms(t1, t2)
                        if t12 is not None:
                            terms.add(t12)

    done = False
    groups: Dict[Tuple[int, int, int], Set[str]] = {}
    while not done:
        # Group terms into groups.
        # groups is a list of length n_groups.
        # Each element of groups is a set of terms with the same
        # number of ones.  In other words, each term contained in the
        # set groups[i] contains exactly i ones.
        groups = {}
        for t in terms:
            n_ones = t.count("1")
            n_xor = t.count("^")
            n_xnor = t.count("~")
            # The algorithm can not cope with mixed XORs and XNORs in
            # one expression.
            assert n_xor == 0 or n_xnor == 0

            key = (n_ones, n_xor, n_xnor)
            if key not in groups:
                groups[key] = set()
            groups[key].add(t)

        terms = set()  # The set of new created terms
        used = set()  # The set of used terms

        # Find prime implicants
        for key in groups:  # pylint: disable=consider-using-dict-items
            key_next = (key[0] + 1, key[1], key[2])
            if key_next in groups:
                group_next = groups[key_next]
                for t1 in groups[key]:
                    # Optimisation:
                    # The Quine-McCluskey algorithm compares t1 with
                    # each element of the next group. (Normal approach)
                    # But in reality it is faster to construct all
                    # possible permutations of t1 by adding a '1' in
                    # opportune positions and check if this new term is
                    # contained in the set groups[key_next].
                    for i, c1 in enumerate(t1):
                        if c1 == "0":
                            profile_cmp += 1
                            t2 = t1[:i] + "1" + t1[i + 1 :]
                            if t2 in group_next:
                                t12 = t1[:i] + "-" + t1[i + 1 :]
                                used.add(t1)
                                used.add(t2)
                                terms.add(t12)

        # Find XOR combinations
        for key in [k for k in groups if k[1] > 0]:
            key_complement = (key[0] + 1, key[2], key[1])
            if key_complement in groups:
                for t1 in groups[key]:
                    t1_complement = t1.replace("^", "~")
                    for i, c1 in enumerate(t1):
                        if c1 == "0":
                            profile_xor += 1
                            t2 = t1_complement[:i] + "1" + t1_complement[i + 1 :]
                            if t2 in groups[key_complement]:
                                t12 = t1[:i] + "^" + t1[i + 1 :]
                                used.add(t1)
                                terms.add(t12)
        # Find XNOR combinations
        for key in [k for k in groups if k[2] > 0]:
            key_complement = (key[0] + 1, key[2], key[1])
            if key_complement in groups:
                for t1 in groups[key]:
                    t1_complement = t1.replace("~", "^")
                    for i, c1 in enumerate(t1):
                        if c1 == "0":
                            profile_xnor += 1
                            t2 = t1_complement[:i] + "1" + t1_complement[i + 1 :]
                            if t2 in groups[key_complement]:
                                t12 = t1[:i] + "~" + t1[i + 1 :]
                                used.add(t1)
                                terms.add(t12)

        # Add the unused terms to the list of marked terms
        for g in list(groups.values()):
            marked |= g - used

        if len(used) == 0:
            done = True

    # Prepare the list of prime implicants
    pi = marked
    for g in list(groups.values()):
        pi |= g
    return ResultWithProfile(result=pi, profile_cmp=profile_cmp, profile_xor=profile_xor, profile_xnor=profile_xnor)


def get_essential_implicants(n_bits: int, terms: Set[str], dc: Set[str]) -> Set[str]:
    """Simplify the set 'terms'.

    Args:
        terms (set of str): set of strings representing the minterms of
        ones and dontcares.
        dc (set of str): set of strings representing the dontcares.

    Returns:
        A list of prime implicants. These are the minterms that cannot be
        reduced with step 1 of the Quine McCluskey method.

    This function is usually called after __get_prime_implicants and its
    objective is to remove non-essential minterms.

    In reality this function omits all terms that can be covered by at
    least one other term in the list.
    """

    # Create all permutations for each term in terms.
    perms: Dict[str, Set[str]] = {}
    for t in terms:
        perms[t] = set(p for p in permutations(t) if p not in dc)

    # Now group the remaining terms and see if any term can be covered
    # by a combination of terms.
    ei_range: Set[str] = set()
    ei: Set[str] = set()
    groups: Dict[int, Set[str]] = {}
    for t1 in terms:
        n = get_term_rank(t1, len(perms[t1]))
        if n not in groups:
            groups[n] = set()
        groups[n].add(t1)
    for t2 in sorted(list(groups.keys()), reverse=True):
        for g in sorted(groups[t2], reverse=True):
            if not perms[g] <= ei_range:
                ei.add(g)
                ei_range |= perms[g]
    if len(ei) == 0:
        ei = set(["-" * n_bits])
    return ei


def get_term_rank(term: str, term_range: int) -> int:
    """Calculate the "rank" of a term.

    Args:
        term (str): one single term in string format.

        term_range (int): the rank of the class of term.

    Returns:
        The "rank" of the term.

    The rank of a term is a positive number or zero.  If a term has all
    bits fixed '0's then its "rank" is 0. The more 'dontcares' and xor or
    xnor it contains, the higher its rank.

    A dontcare weights more than a xor, a xor weights more than a xnor, a
    xnor weights more than 1 and a 1 weights more than a 0.

    This means, the higher rank of a term, the more desireable it is to
    include this term in the final result.
    """
    n = 0
    for t in term:
        if t == "-":
            n += 8
        elif t == "^":
            n += 4
        elif t == "~":
            n += 2
        elif t == "1":
            n += 1
    return 4 * term_range + n


def permutations(value: str = "", exclude: Set[str] = set()) -> Set[str]:
    """Iterator to generate all possible values out of a string.

    Args:
        value (str): A string containing any of the above characters.
        exclude (set): A set of values to skip (usually don't cares)

    Returns:
        The output strings contain only '0' and '1'.

    Example:
        from qm import QuineMcCluskey
        qm = QuineMcCluskey()
        for i in qm.permutations('1--^^'):
            print(i)

    The operation performed by this generator function can be seen as the
    inverse of binary minimisation methonds such as Karnaugh maps, Quine
    McCluskey or Espresso.  It takes as input a minterm and generates all
    possible maxterms from it.  Inputs and outputs are strings.

    Possible input characters:
        '0': the bit at this position will always be zero.
        '1': the bit at this position will always be one.
        '-': don't care: this bit can be zero or one.
        '^': all bits with the caret are XOR-ed together.
        '~': all bits with the tilde are XNOR-ed together.

    Algorithm description:
        This lovely piece of spaghetti code generates all possibe
        permutations of a given string describing logic operations.
        This could be achieved by recursively running through all
        possibilities, but a more linear approach has been preferred.
        The basic idea of this algorithm is to consider all bit
        positions from 0 upwards (direction = +1) until the last bit
        position. When the last bit position has been reached, then the
        generated string is yielded.  At this point the algorithm works
        its way backward (direction = -1) until it finds an operator
        like '-', '^' or '~'.  The bit at this position is then flipped
        (generally from '0' to '1') and the direction flag again
        inverted. This way the bit position pointer (i) runs forth and
        back several times until all possible permutations have been
        generated.
        When the position pointer reaches position -1, all possible
        combinations have been visited.
    """
    exclude_int: Set[int] = {int(e) for e in exclude}
    n_bits = len(value)
    n_xor = value.count("^") + value.count("~")
    xor_value = 0
    seen_xors = 0
    res = ["0" for i in range(n_bits)]
    i = 0
    direction = +1
    result: Set[str] = set()
    while i >= 0:
        # binary constant
        if value[i] == "0" or value[i] == "1":
            res[i] = value[i]
        # dontcare operator
        elif value[i] == "-":
            if direction == +1:
                res[i] = "0"
            elif res[i] == "0":
                res[i] = "1"
                direction = +1
        # XOR operator
        elif value[i] == "^":
            seen_xors = seen_xors + direction
            if direction == +1:
                if seen_xors == n_xor and xor_value == 0:
                    res[i] = "1"
                else:
                    res[i] = "0"
            else:
                if res[i] == "0" and seen_xors < n_xor - 1:
                    res[i] = "1"
                    direction = +1
                    seen_xors = seen_xors + 1
            if res[i] == "1":
                xor_value = xor_value ^ 1
        # XNOR operator
        elif value[i] == "~":
            seen_xors = seen_xors + direction
            if direction == +1:
                if seen_xors == n_xor and xor_value == 1:
                    res[i] = "1"
                else:
                    res[i] = "0"
            else:
                if res[i] == "0" and seen_xors < n_xor - 1:
                    res[i] = "1"
                    direction = +1
                    seen_xors = seen_xors + 1
            if res[i] == "1":
                xor_value = xor_value ^ 1
        # unknown input
        else:
            res[i] = "#"

        i = i + direction
        if i == n_bits:
            direction = -1
            i = n_bits - 1
            bitstring = "".join(res)
            if int(bitstring, base=2) not in exclude_int:
                result.add(bitstring)

    return result


def get_terms(implicant: str) -> Tuple[List[int], List[int], List[int], List[int], List[int]]:
    """Return the indexes for each type of token in given implicant string"""
    term_ones = [m.start() for m in re.finditer(re.escape("1"), implicant)]
    term_zeros = [m.start() for m in re.finditer(re.escape("0"), implicant)]
    term_xors = [m.start() for m in re.finditer(re.escape("^"), implicant)]
    term_xnors = [m.start() for m in re.finditer(re.escape("~"), implicant)]
    term_dcs = [m.start() for m in re.finditer(re.escape("-"), implicant)]
    return term_ones, term_zeros, term_xors, term_xnors, term_dcs


def complexity(implicant: str) -> float:
    """Helper function deternining the order of the implicants.

    Args:
        implicant (str): Implicant

    Returns:
        float: Estimated complexity.
    """
    ret: float = 0
    term_ones, term_zeros, term_xors, term_xnors, _ = get_terms(implicant)
    ret += 1.00 * len(term_ones)
    ret += 1.50 * len(term_zeros)
    ret += 1.25 * len(term_xors)
    ret += 1.75 * len(term_xnors)
    return ret


def combine_implicants(a: str, b: str, dc: Set[str]) -> Optional[str]:
    """Combine two implicants.

    Args:
        a (str): First implicant.
        b (str): Second implicant.
        dc (Set[str]): Don't care set.

    Returns:
        Optional[str]: Combined implicants. None if invalid.
    """
    permutations_a = set(permutations(a, exclude=dc))
    permutations_b = set(permutations(b, exclude=dc))
    _, _, _, _, a_term_dcs = get_terms(a)
    _, _, _, _, b_term_dcs = get_terms(b)
    a_potential, b_potential = list(a), list(b)
    for index in a_term_dcs:
        a_potential[index] = b[index]
    for index in b_term_dcs:
        b_potential[index] = a[index]
    valid = [
        x
        for x in ["".join(a_potential), "".join(b_potential)]
        if permutations(x, exclude=dc) == (permutations_a | permutations_b)
    ]
    if valid:
        return min(valid, key=complexity)
    return None


def reduce_implicants(n_bits: int, implicants: Set[str], dc: Set[str]) -> Set[str]:
    """Perform further reduction on essential implicants.

    Args:
        n_bits (int): Number of bits of the input.
        implicants (Set[str]): Implicants
        dc (Set[str]): Don't care set.

    Returns:
        Set[str]: Reduced implicants.
    """
    # Combine implicants in orthogonal spaces
    while True:
        for a, b in itertools.combinations(implicants, 2):
            replacement = combine_implicants(a, b, dc=dc)
            if replacement:
                implicants.remove(a)
                implicants.remove(b)
                implicants |= {replacement}
                break
        else:
            break

    # Reduce redundant implicants further by comparing their coverage
    coverage: Dict[str, Set[str]] = {
        implicant: {n for n in permutations(implicant) if n not in dc} for implicant in implicants
    }

    while True:
        redundant = []
        for this_implicant in list(coverage):
            this_coverage = coverage[this_implicant]
            others_coverage = {
                n
                for other_implicant in [implicant for implicant in coverage.keys() if implicant != this_implicant]
                for n in coverage[other_implicant]
            }
            if this_coverage.issubset(others_coverage):
                redundant.append(this_implicant)
        if redundant:
            worst = sorted(redundant, key=complexity, reverse=True)[0]
            del coverage[worst]
        else:
            break
    if not coverage:
        coverage = {"-" * n_bits: set()}
    return set(coverage.keys())


def simplify_los_with_profile(
    ones: Iterable[str], dc: Iterable[str] = [], num_bits: Optional[int] = None, use_xor: bool = True
) -> ResultWithProfile:
    """Implementation for the simplify_los function."""

    terms: Set[str] = set(ones) | set(dc)
    if len(terms) == 0:
        return ResultWithProfile.none

    # Calculate the number of bits to use
    if num_bits is not None:
        n_bits = num_bits
    else:
        n_bits = max(len(i) for i in terms)
        if n_bits != min(len(i) for i in terms):
            return ResultWithProfile.none

    # First step of Quine-McCluskey method.
    prime_implicants = get_prime_implicants(n_bits=n_bits, use_xor=use_xor, terms=terms)

    # Remove essential terms.
    assert prime_implicants.result is not None
    essential_implicants = get_essential_implicants(n_bits=n_bits, terms=prime_implicants.result, dc=set(dc))

    # Perform further reduction on essential implicants
    reduced_implicants = reduce_implicants(n_bits=n_bits, implicants=essential_implicants, dc=set(dc))

    return ResultWithProfile(
        result=reduced_implicants,
        profile_cmp=prime_implicants.profile_cmp,
        profile_xor=prime_implicants.profile_xor,
        profile_xnor=prime_implicants.profile_xnor,
    )


def simplify_with_profile(
    ones: List[int], dc: List[int] = [], num_bits: Optional[int] = None, use_xor: bool = False
) -> ResultWithProfile:
    """Implementation for the simplify function."""
    terms = ones + dc
    if len(terms) == 0:
        return ResultWithProfile.none

    # Calculate the number of bits to use
    # Needed internally by __num2str()
    n_bits = num_bits
    if n_bits is None:
        n_bits = int(math.ceil(math.log(max(terms) + 1, 2)))

    # Generate the sets of ones and dontcares
    ones_processed = [num2str(n_bits, i) for i in ones]
    dc_processed = [num2str(n_bits, i) for i in dc]

    return simplify_los_with_profile(ones_processed, dc_processed, num_bits=num_bits, use_xor=use_xor)


def simplify(ones: List[int], dc: List[int] = [], num_bits: Optional[int] = None, use_xor: bool = False) -> Optional[Set[str]]:
    """The simplification algorithm for a list of string-encoded inputs.

    Args:
        ones (list of str): list of strings that describe when the output
        function is '1', e.g. ['0001', '0010', '0110', '1000', '1111'].

    Kwargs:
        dc: (list of str): list of strings that define the don't care
        combinations.

    Returns:
        Returns a set of strings which represent the reduced minterms.  The
        length of the strings is equal to the number of bits in the input.
        Character 0 of the output string stands for the most significant
        bit, Character n - 1 (n is the number of bits) stands for the least
        significant bit.

        The following characters are allowed in the return string:
            '-' don't care: this bit can be either zero or one.
            '1' the bit must be one.
            '0' the bit must be zero.
            '^' all bits with the caret are XOR-ed together.
            '~' all bits with the tilde are XNOR-ed together.

    Example:
        ones = ['0010', '0110', '1010', '1110']
        dc = []

        This will produce the ouput: ['--10'].
        In other words, x = b1 & ~b0, (bit1 AND NOT bit0).

    Example:
        ones = ['0001', '0010', '0101', '0110', '1001', '1010' '1101', '1110']
        dc = []

        This will produce the ouput: ['--^^'].
        In other words, x = b1 ^ b0, (bit1 XOR bit0).
    """
    return simplify_with_profile(ones=ones, dc=dc, num_bits=num_bits, use_xor=use_xor).result


def simplify_los(
    ones: Iterable[str], dc: Iterable[str] = [], num_bits: Optional[int] = None, use_xor: bool = False
) -> Optional[Set[str]]:
    """Simplify a list of terms.

    Args:
        ones (list of int): list of integers that describe when the output
        function is '1', e.g. [1, 2, 6, 8, 15].

    Kwargs:
        dc (list of int): list of numbers for which we don't care if they
        have one or zero in the output.

    Returns:
        see: simplify_los.

    Example:
        ones = [2, 6, 10, 14]
        dc = []

        This will produce the ouput: ['--10']
        This means x = b1 & ~b0, (bit1 AND NOT bit0)

    Example:
        ones = [1, 2, 5, 6, 9, 10, 13, 14]
        dc = []

        This will produce the ouput: ['--^^'].
        In other words, x = b1 ^ b0, (bit1 XOR bit0).
    """
    return simplify_los_with_profile(ones=ones, dc=dc, num_bits=num_bits, use_xor=use_xor).result
