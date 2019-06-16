#!/bin/sh
set -e

name=`python setup.py --name`
version=`python setup.py --version`
archive="$name-v$version"

# rm -rf quine_mccluskey.egg-info build cmp dist

git archive --format=tar --prefix="$archive/" HEAD | tar x
rm -f "$archive/$0"

tar cvzf "$archive.tar.gz" "$archive"
zip "$archive.zip" "$archive"
rm -rf "$archive"
