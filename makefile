include $(INI_HOME)/common.mk

export CHAP_DIR = chaps

.PHONY: html web github

# build the HTML versions of the chapters into _site/
html:
	bin/site

web: html github

github:
	-git commit -a
	git push origin main

book.md: $(CHAP_DIR)/*.md
	cat $^ > $@

book.docx: book.md
	pandoc -o $@ -f markdown -t docx $^
