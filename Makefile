PREFIX ?= /usr/local
BINDIR = $(DESTDIR)$(PREFIX)/bin
MANDIR = $(DESTDIR)$(PREFIX)/share/man/man1
DOCDIR = $(DESTDIR)$(PREFIX)/share/doc/ddgr

.PHONY: all install uninstall

all:

install:
	install -m755 -d $(BINDIR)
	install -m755 -d $(MANDIR)
	install -m755 -d $(DOCDIR)
	gzip -c ddgr.1 > ddgr.1.gz
	install -m755 ddgr $(BINDIR)
	install -m644 ddgr.1.gz $(MANDIR)
	install -m644 README.md $(DOCDIR)
	rm -f ddgr.1.gz

uninstall:
	rm -f $(BINDIR)/ddgr
	rm -f $(MANDIR)/ddgr.1.gz
	rm -rf $(DOCDIR)

test: ;
