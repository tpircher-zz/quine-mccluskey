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
terms. This slows down the algorithm, but in some cases the result can be much
more compact than a sum of product.


How to install qm.py
--------------------

Install the package with

 python setup.py install

This needs superuser privileges. If you want to install the package locally,
you can run:

 mypath=XXX
 PYTHONPATH=$mypath/lib/python2.7/site-packages/ python setup.py install --prefix $mypath

where XXX can be any path. You may have to change the PYTHONPATH according to your
python version.
