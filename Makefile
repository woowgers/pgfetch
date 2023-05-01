SRC_DIR = src
MAIN_MODULE = project.main
MAIN_SOURCE = $(SRC_DIR)/$(subst .,/,$(MAIN_MODULE)).py
TESTS_DIR = $(SRC_DIR)/tests
ANY_TEST = $(TESTS_DIR)/**/test_*.py


run: $(MAIN_SOURCE)
	cd $(SRC_DIR) && python -m $(MAIN_MODULE)


test: $(ANY_TEST)
	pytest


coverage: $(ANY_TEST)
	coverage run -m pytest
	coverage json
