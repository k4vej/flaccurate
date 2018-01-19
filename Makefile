copy_vim_files:
	@if [ ! -d "./.vim" ]; then cp -r -L "$$HOME/.vim" ./.vim; fi
	@if [ ! -f "./.vimrc" ]; then cp -L "$$HOME/.vimrc" ./.vimrc; fi

remove_vim_files:
	@rm -rf ./.vim
	@rm ./.vimrc

remove_nuitka_files:
	@rm -fr flaccurate.build
	@rm -fr flaccurate.dist

build: copy_vim_files
	@docker build -t python-container-with-vim .

run: build
	@docker run -it -v "$$(pwd)":/app python-container-with-vim /bin/bash

clean: remove_vim_files remove_nuitka_files
	-@docker rmi -f python-container-with-vim &> /dev/null || true

test:
	PYTHONPATH=. pytest

dist:
	nuitka-run --standalone --show-modules --show-progress --recurse-on --python-flag=no_site --python-version=3.6 flaccurate.py

dist-clean: remove_nuitka_files

rebuild: clean run
