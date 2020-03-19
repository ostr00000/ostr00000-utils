MAIN_PACKAGE_NAME=pyqt_utils

UIC=pyuic5
RCC=pyrcc5

UI_DIR=src/ui
COMPILED_UI_DIR=lib/$(MAIN_PACKAGE_NAME)/ui
RESOURCES=src/resources.qrc
####################################

UI_FILES=$(wildcard $(UI_DIR)/*.ui)
COMPILED_UI_FILES=$(UI_FILES:$(UI_DIR)/%.ui=$(COMPILED_UI_DIR)/ui_%.py)
RESOURCES_SRC=$(shell grep '^ *<file' $(RESOURCES) | sed 's@</file>@@g;s@.*>@src/@g' | tr '\n' ' ')

define RESOURCE_CONTENT
<RCC>
  <qresource>
    <file></file>
  </qresource>
</RCC>
endef
export RESOURCE_CONTENT

all: ui resources
	@echo "Make all finished"


main_dir:
	mkdir -p lib/$(MAIN_PACKAGE_NAME)

ui: $(COMPILED_UI_FILES)

$(COMPILED_UI_DIR)/ui_%.py : $(UI_DIR)/%.ui
	mkdir -p $(COMPILED_UI_DIR)
	$(UIC) $< --from-imports -o $@

resources: $(COMPILED_UI_DIR)/resources_rc.py

$(COMPILED_UI_DIR)/resources_rc.py: $(RESOURCES) $(RESOURCES_SRC)
	mkdir -p $(COMPILED_UI_DIR)
	echo 'from . import resources_rc' > $(COMPILED_UI_DIR)/__init__.py
	$(RCC) -o $(COMPILED_UI_DIR)/resources_rc.py  $<

$(RESOURCES):
	mkdir -p 'src/icons'
	mkdir -p 'src/ui'
	echo "$$RESOURCE_CONTENT" > $@

.PHONY: all ui resources compile
