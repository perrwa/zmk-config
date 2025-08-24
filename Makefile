# Makefile for packaging and flashing MDBT50Q-CX-40 Dongle

# References
# https://docs.zephyrproject.org/latest/boards/raytac/mdbt50q_cx_40_dongle/doc/index.html#

# Variables
DIR        ?= ./firmware
NRFUTIL    ?= nrfutil nrf5sdk-tools

KEY_FILE   ?= private.pem
BIN_FILES  := $(wildcard $(DIR)/*.bin)
ZIP_FILES  := $(BIN_FILES:.bin=.zip)

# DEFAULT AND PHONY TARGETS
.DEFAULT_GOAL := help
.PHONY: dfu flash clean help

help:  ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

dfu: has_key clean  ## Create DFU packages from .bin files
	@for bin in $(BIN_FILES); do \
		zip="$${bin%.bin}.zip"; \
		echo "Creating DFU package: $$zip"; \
		$(NRFUTIL) pkg generate \
			--hw-version 52 \
			--sd-req=0x00 \
			--key-file "$(KEY_FILE)" \
			--application "$$bin" \
			--application-version 1 \
			"$$zip"; \
	done

flash:  ## Flash a selected DFU package to a selected serial port
	@SERIALS=($(shell ls /dev/tty.usb* 2>/dev/null)); \
	if [ $${#SERIALS[@]} -eq 0 ]; then \
		echo "No /dev/tty.usb* serial ports found."; exit 1; \
	fi; \
	echo "\nAvailable serial ports:"; \
	for i in $${!SERIALS[@]}; do echo "$$((i+1)): $${SERIALS[$$i]}"; done; \
	read -p "Select serial port [1-$${#SERIALS[@]}]: " idx; \
	PORT=$${SERIALS[$$(($$idx-1))]}; \
	ZIPS=($(shell ls $(DIR)/*.zip 2>/dev/null)); \
	if [ $${#ZIPS[@]} -eq 0 ]; then \
		echo "No .zip DFU packages found in $(DIR)."; exit 1; \
	fi; \
	echo "\nAvailable DFU packages:"; \
	for i in $${!ZIPS[@]}; do echo "$$((i+1)): $${ZIPS[$$i]}"; done; \
	read -p "Select DFU package [1-$${#ZIPS[@]}]: " zidx; \

	PKG=$${ZIPS[$$(($$zidx-1))]}; \
	echo "\nFlashing $$PKG to $$PORT..."; \
	$(NRFUTIL) dfu usb-serial -pkg \"$$PKG\" -p \"$$PORT\"

clean:  ## Remove all generated .zip DFU packages
	@rm -f $(DIR)/*.zip

has_key:  ## Check if the key file exists
	@if [ ! -f "$(KEY_FILE)" ]; then \
		$(NRFUTIL) keys generate $(KEY_FILE); \
	fi
