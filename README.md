qm.py
=====

A Python implementation of the Quine McCluskey algorithm.

This implementation of the Quine McCluskey algorithm has no inherent limits
(other than the calculation time) on the size of the inputs.

Also, in the limited tests of the author of this module, this implementation is
considerably faster than other public Python implementations for non-trivial
inputs.

Another unique feature of this implementation is the possibility to use the XOR
and XNOR operators, in addition to the normal AND operator, to minimise the
terms. This slows down the algorithm, but in some cases it can be a big win in
terms of complexity of the output.
