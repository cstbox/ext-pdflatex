# Makefile for building the Debian distribution package containing the
# PdfLaTex extension.

# author = Eric PASCUAL - CSTB (eric.pascual@cstb.fr)
# version = 1.0.0

# name of the CSTBox module
MODULE_NAME=ext-pdflatex

include $(CSTBOX_DEVEL_HOME)/lib/makefile-dist.mk

copy_files: \
	copy_python_files \
	copy_etc_files