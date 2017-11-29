PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/share/man/man1
DOCDIR ?= $(PREFIX)/share/doc/ddgr

.PHONY: all install uninstall

all:

install:
	install -m755 -d $(DESTDIR)$(BINDIR)
	install -m755 -d $(DESTDIR)$(MANDIR)
	install -m755 -d $(DESTDIR)$(DOCDIR)
	gzip -c ddgr.1 > ddgr.1.gz
	install -m755 ddgr $(DESTDIR)$(BINDIR)
	install -m644 ddgr.1.gz $(DESTDIR)$(MANDIR)
	install -m644 README.md $(DESTDIR)$(DOCDIR)
	rm -f ddgr.1.gz

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/ddgr
	rm -f $(DESTDIR)$(MANDIR)/ddgr.1.gz
	rm -rf $(DESTDIR)$(DOCDIR)

test:
	./ddgr --help
