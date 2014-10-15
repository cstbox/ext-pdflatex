#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Eric Pascual - CSTB (eric.pascual@cstb.fr)'

import os
import subprocess
import json

from pycstbox.log import Loggable
from pycstbox import sysutils

DEFAULT_OUTPUT_DIR = "/tmp/cstbox/reports"
DEFAULT_CONFIG_PATH = "/etc/cstbox/pdflatex.cfg"


class PDFLaTeX(Loggable):
    CFG_KEY_PDFLATEX_PATH = "pdflatex_path"

    DEFAULT_PDFLATEX_PATH = '/usr/local/texlive/2014/bin/i386-linux/pdflatex'

    def __init__(self, config_path=DEFAULT_CONFIG_PATH):
        super(PDFLaTeX, self).__init__()

        settings = json.load(file(config_path, 'rt'))
        self._pdflatex_bin = settings.get(self.CFG_KEY_PDFLATEX_PATH, self.DEFAULT_PDFLATEX_PATH)
        if not os.path.isfile(self._pdflatex_bin):
            raise ValueError('file not found : %s' % self._pdflatex_bin)

    def compile(self, source, output_dir=None):
        if not source:
            raise ValueError('missing source parameter')
        if not os.path.exists(source):
            raise ValueError('path not found : %s' % source)
        if not os.path.isfile(source):
            raise ValueError('path is not a file : %s' % source)

        if not output_dir:
            output_dir = os.path.dirname(os.path.abspath(source))

        pdf_file_path = os.path.join(
            output_dir,
            os.path.basename(source).replace('.tex', '.pdf')
        )
        if os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)

        try:
            command = "cd %(output_dir)s && %(pdflatex_bin)s -interaction=nonstopmode %(source)s" % {
                'pdflatex_bin': self._pdflatex_bin,
                'output_dir': output_dir,
                'source': source
            }
            subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as e:
            if e.returncode == 127:
                raise PdfLaTeXError('pdflatex command not found')
            else:
                error_marker = '! LaTeX Error:'
                latex_errors = [l.lstrip(error_marker) for l in e.output.split('\n') if l.startswith(error_marker)]
                raise PdfLaTeXError(str(e), latex_errors)

        else:
            return pdf_file_path


    @staticmethod
    def pgfplot(plot_name, axis_options, plot_options, points, output_dir=DEFAULT_OUTPUT_DIR):
        for parm_name in ('axis_options', 'plot_options'):
            if not locals()[parm_name]:
                raise ValueError('%s parameter is mandatory' % parm_name)
        if not isinstance(points, list):
            raise TypeError('points parameter type mismatch')

        script = r"""
            \begin{axis}[
              date coordinates in=x,
              grid=major,
              %(axis_options)s
            ]
            \addplot [%(plot_options)s] coordinates {
            %(coordinates)s
            };
            \end{axis}
        """ % {
            'axis_options': axis_options,
            'plot_options': plot_options,
            'coordinates': '\n'.join("(%s, %f)" % (
                sysutils.ts_to_datetime(x).strftime('%Y-%m-%d %H:%M'), y) for x, y in points
            )
        }

        script_file = os.path.join(output_dir, 'pgfplot-' + plot_name + '.tex')
        with file(script_file, 'wt') as f:
            for line in sysutils.string_to_lines(script):
                f.write(line + '\n')

        return script_file


class PdfLaTeXError(Exception):
    def __init__(self, msg, errors=None):
        super(PdfLaTeXError, self).__init__(msg)
        self.latex_errors = errors
