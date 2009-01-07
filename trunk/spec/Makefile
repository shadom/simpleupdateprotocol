NAME=draft-clinton-sup
REV=current
SOURCE=$(NAME)
TARGET=$(NAME)-$(REV)

default: $(TARGET).html $(TARGET).txt nits

$(TARGET).html: $(SOURCE).xml xml2rfc.tcl
	tclsh8.4 xml2rfc.tcl xml2html $(SOURCE).xml  $(TARGET).html

$(TARGET).txt:  $(SOURCE).xml xml2rfc.tcl
	tclsh8.4 xml2rfc.tcl xml2rfc $(SOURCE).xml $(TARGET).txt

.PHONY: nits
nits:
	./idnits --verbose $(TARGET).txt

