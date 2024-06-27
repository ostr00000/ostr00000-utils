MAIN_PACKAGE_NAME=pyqt_utils

UIC=pyuic5
UI_DIR=src/$(MAIN_PACKAGE_NAME)/ui
UI_FILES=$(wildcard $(UI_DIR)/*.ui)
COMPILED_UI_FILES=$(UI_FILES:$(UI_DIR)/%.ui=$(UI_DIR)/%_ui.py)

PYTHON_ENV=../manager_env/bin/python

####################################
.PHONY: all ui

all: ui
	@echo "Make all finished"

ui: $(COMPILED_UI_FILES)

$(UI_DIR)/%_ui.py : $(UI_DIR)/%.ui
	$(UIC) $< --from-imports -o $@


# ######## pre-commit ########
.PHONY: pre_commit pre_commit_install pre_commit_uninstall pre_commit_auto_update

pre_commit:
	$(PYTHON_ENV) -m pre_commit run --all-files

pre_commit_install:
	$(PYTHON_ENV) -m pre_commit install

pre_commit_uninstall:
	$(PYTHON_ENV) -m pre_commit uninstall

pre_commit_auto_update:
	$(PYTHON_ENV) -m pre_commit autoupdate

pre_commit_gc:
	$(PYTHON_ENV) -m pre_commit gc

# ######## checks ########
.PHONY: check_by_mypy check_by_pyright check_by_pylint

check_by_mypy:
	$(PYTHON_ENV) -m mypy

check_by_pyright:
	$(PYTHON_ENV) -m pyright

check_by_pylint:
	$(PYTHON_ENV) -m pylint ./lib/
