# SPDX-License-Identifier: GPL-3.0-or-later
# Build the iec104_cli payload with PyInstaller.
#
#   make build/local     build for the host platform (needs a local venv)
#   make build/linux     build a Linux binary in a pinned Docker image
#   make build/windows   build a Windows binary in a pinned Docker image
#   make update          copy freshly built binaries into ../payloads
#   make clean           remove build artifacts
#
# The distributed binaries are produced by the GitHub Actions matrix
# (.github/workflows/ci.yaml); these targets reproduce them locally.

PYI := pyinstaller --clean iec104_cli.spec
DOCKER_LINUX := batonogov/pyinstaller-linux:latest
DOCKER_WINDOWS := batonogov/pyinstaller-windows:latest

.PHONY: build/local build/linux build/windows update clean

build/local:
	pip install -r requirements.txt pyinstaller
	$(PYI)

build/linux:
	docker run --rm --volume "$(CURDIR):/src/" --entrypoint /bin/sh $(DOCKER_LINUX) \
		-c "pip install -r requirements.txt && $(PYI)"

build/windows:
	docker run --rm --volume "$(CURDIR):/src/" --entrypoint /bin/sh $(DOCKER_WINDOWS) \
		-c "pip install -r requirements.txt && $(PYI)"

update:
	cp dist/* ../payloads/

clean:
	rm -rf build dist __pycache__ iec104/__pycache__
