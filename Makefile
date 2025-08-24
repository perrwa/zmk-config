# Makefile for packaging and flashing MDBT50Q-CX-40 Dongle

# References
# https://docs.zephyrproject.org/latest/boards/raytac/mdbt50q_cx_40_dongle/doc/index.html#

# Variables
DIR        ?= .
NRFUTIL    ?= nrfutil nrf5sdk-tools

BIN_FILES  := $(wildcard $(DIR)/*.bin)
ZIP_FILES  := $(BIN_FILES:.bin=.zip)

.PHONY: all dfu flash clean

all: dfu

dfu:
	@for bin in $(BIN_FILES); do \
		zip="$${bin%.bin}.zip"; \
		echo "Creating DFU package: $$zip"; \
		$(NRFUTIL) pkg generate \
			--hw-version 52 \
			--sd-req=0x00 \
			--application "$$bin" \
			--application-version 1 \
			"$$zip"; \
	done

flash:
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

clean:
	rm -f $(DIR)/*.zip
