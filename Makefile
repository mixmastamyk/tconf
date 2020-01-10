
include ../../Makefile.common

test:
	pyflakes *.py tconf/*.py tests/*.py
	cd tests; python3 test.py
	cd tests; python3 test_arg_cfg.py
	cd tests; python3 test_seqs.py

