# Copyright (c) 2020 Xvezda <xvezda@naver.com>
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

.PHONY: test build clean check publish


PY = python
PY2 = python2
PY3 = python3
TWINE = twine

TR = tr
RM = rm
CUT = cut
SED = sed
FIND = find
HEAD = head
GREP = grep
XARGS = xargs
PKG_NAME = $(shell $(FIND) . -maxdepth 2 -name '__init__.py' | $(CUT) -d'/' -f2 | $(HEAD) -n1)
METADATA_FILE = $(PKG_NAME)/__about__.py
PKG_VERSION = $(shell $(SED) -n -E "s/__version__ = [\"']([^\"']+)[\"']/\1/p" $(METADATA_FILE))
DIST_DIR = dist
DIST_FILES = $(wildcard $(DIST_DIR)/$(PKG_NAME)-$(PKG_VERSION)*)
TEST_DIR = tests


all: clean build

build: py2dist py3dist

py2dist:
	$(PY2) setup.py sdist bdist_wheel

py3dist:
	$(PY3) setup.py sdist bdist_wheel

check:
	$(TWINE) check $(DIST_DIR)/$(PKG_NAME)-$(PKG_VERSION)*

publish: all check
	$(TWINE) upload $(DIST_FILES)

pkg_version:
	@echo $(PKG_VERSION)

clean:
	$(GREP) '/$$' .gitignore \
		| $(XARGS) -I{} echo "\\! -path '*/{}*'" \
		| $(TR) $$'\n' ' ' | $(XARGS) $(FIND) . -name '*.pyc' \
		| $(XARGS) -n1 $(RM)
	$(PY) setup.py clean
	$(RM) -rf build/

