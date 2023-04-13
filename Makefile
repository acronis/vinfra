DESTDIR =
PYTHONPATH := $(DESTDIR)/$(shell python -c "import sysconfig; print(sysconfig.get_path('purelib'))")
SYSCONFDIR = $(DESTDIR)/etc
BASHCOMPLETIONDIR = $(SYSCONFDIR)/bash_completion.d
LOGROTATEDIR = $(SYSCONFDIR)/logrotate.d
LOGROTATEFILE = vinfra.logrotate

get_version:
	python build/version.py --action=get

increase_version:
	python build/version.py --action=inc

complete:
	@python build/complete.py

build:
	mkdir -p ${BUILD_UPLOAD_PATH}; tar --exclude='./.git' --exclude=${BUILD_UPLOAD_PATH} -zcvf ${BUILD_UPLOAD_PATH}/archive.tgz .

test:
	./test.sh

install:
	for d in $(BASHCOMPLETIONDIR) $(LOGROTATEDIR); do mkdir -p $$d ; done
	PYTHONPATH=$(PYTHONPATH) make -s complete > $(BASHCOMPLETIONDIR)/vinfra
	install -m 644 $(LOGROTATEFILE) $(LOGROTATEDIR)/vinfra
