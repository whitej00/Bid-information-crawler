import subprocess
import sys
import glob
import os
import time
from errno import ENOENT
from os import environ, extsep, remove

def subprocess_args(include_stdout=True):
    # See https://github.com/pyinstaller/pyinstaller/wiki/Recipe-subprocess
    # for reference and comments.

    kwargs = {
        'stdin': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'startupinfo': None,
        'env': environ,
    }

    if hasattr(subprocess, 'STARTUPINFO'):
        kwargs['startupinfo'] = subprocess.STARTUPINFO()
        kwargs['startupinfo'].dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs['startupinfo'].wShowWindow = subprocess.SW_HIDE

    if include_stdout:
        kwargs['stdout'] = subprocess.PIPE

    return kwargs

def run_tesseract(
    input_filename,
    output_filename_base,
    extension,
    lang,
    config='',
    nice=0,
    timeout=0,
    duple=0,
):

    cmd_args = []

    if not sys.platform.startswith('win32') and nice != 0:
        cmd_args += ('nice', '-n', str(nice))

    cmd_args += ('tesseract', input_filename, output_filename_base)

    if lang is not None:
        cmd_args += ('-l', lang)

    if config:
        cmd_args += shlex.split(config)

    if extension and extension not in {'box', 'osd', 'tsv', 'xml'}:
        cmd_args.append(extension)

    try:
        proc = subprocess.Popen(cmd_args, **subprocess_args())
    except OSError as e:
        if e.errno != ENOENT:
            raise e
        raise TesseractNotFoundError()
    
    if duple % 3 == 0 and not proc.wait(timeout = None):
        pass

    # with timeout_manager(proc, timeout) as error_string:
    #     if proc.returncode:
    #         raise TesseractError(proc.returncode, get_errors(error_string))

def file_list(fetchall):
    i = 0
    path_names = []
    globs = []
    target_dir = "/srv1/process/Files/{0}/*.jpg"
    for fetch in fetchall:
        globs = glob.glob(target_dir.format(fetch[0]), recursive=True)
        for a in globs:
            path_names.append(a)

    for path_name in path_names:
        i += 1
        print(path_name)
        dirname = os.path.dirname(path_name)
        basename = os.path.basename(path_name)
        filename = '.'.join(basename.split('.')[:-1])
        kwargs = {
                'input_filename': path_name,
                'output_filename_base': dirname + '/' + filename,
                'extension': 'txt',
                'lang': 'eng',
                'config': '',
                'nice': 0,
                'timeout': 0,
                'duple' : i,
            }
        run_tesseract(**kwargs)  