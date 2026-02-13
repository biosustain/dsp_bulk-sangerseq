import os
import shutil

def copy_files(src_file: str, dest_file: str):
    """Copies single files from source to destination folder.
    Args:
        src_file (str): Path to source file.
        dest_file (str): Path to destination file.
    """
    shutil.copy2(src_file, dest_file)


def copy_files_extension(src_dir: str, dest_dir: str, file_ext: tuple):
    """Copies file of specified extension types from source to destination directory
    Args:
        src_dir (str): Path to source directory.
        dest_dir (str): Path to destination directory.
        file_ext (tuple): file name extensions, e.g. ('.json', '.html').
    """
    if len(os.listdir(src_dir)) > 0:    #check if directory contains files
        for filename in os.listdir(src_dir):
            if filename.endswith(file_ext):
                shutil.copy2(os.path.join(src_dir , filename), dest_dir)