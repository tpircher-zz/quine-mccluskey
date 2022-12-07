qm.py
=====

![build](https://github.com/tomas789/quine-mccluskey-tomas789/actions/workflows/python-package.yml/badge.svg)


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


## Installation

The recommanded way of installing this package is by using pip

```bash
python3 -m pip install quine-mccluskey-tomas789
```

Note that on Windows you might need to use the `py` command instead.

```bash
py -m pip install quine-mccluskey-tomas789
```

There are some othere means of installing the package which are recommanded only in specific cases.

### Development build

```bash
python3 -m pip install -e .
```

### Build wheel files locally

Make sure you have the latest version of PyPA's build installed:

```bash
python3 -m pip install --upgrade build
```

Now run this command from the same directory where pyproject.toml is located:

```bash
python3 -m build
```

This command should output a lot of text and once completed should generate two files in the dist directory:

```text
dist/
├── quine_mccluskey_tomas789-1.0-py2.py3-none-any.whl
└── quine_mccluskey_tomas789-1.0.tar.gz
```

Wheel file can then be distributed via your own means and installed using pip

```bash
python3 -m pip install dist/quine_mccluskey_tomas789-1.0-py2.py3-none-any.whl
```

## Running tests

### Unit tests

The library comes with a basic set of unit tests. They can be executed using `pytest`

```bash
pytest
```

### Fuzz testing

We also have a fuzz testing. It generates random formulas, simplifies them and checks that the result is correct. 

```bash
➜  quine-mccluskey-tomas789 git:(main) python fuzz.py   
Checked 24300 formulas and found 0 errors.
Checked 48400 formulas and found 0 errors.
Checked 72300 formulas and found 0 errors.
Checked 96300 formulas and found 0 errors.
Testing formulas ... ⠋ 0:00:44
```

