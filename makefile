include $(INI_HOME)/common.mk

export CHAP_DIR = chaps

github:
	-git commit -a
	git push origin main

book.md: $(CHAP_DIR)/*.md
	cat $^ > $@

book.docx: book.md
	pandoc -o $@ -f markdown -t docx $^
