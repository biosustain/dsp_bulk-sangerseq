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



def convert_files_to_markdown_read_write(src_dir_path: str, 
                                        src_file_ext: str | tuple[str, ...], 
                                        dest_dir_path: str
                                        ):
    """
    Read file with specified file type from source directory, convert to markdown and save to a destination directory.
    
    Args:
        src_dir_path: path to source directory holding files to be converted
        src_file_ext: extension of files to be converted, e.g. '.align1' or ('.align1', '.align2', '.align3')
        dest_dir_path: path to sdestination directory the .md files will be saved to
    """

    try: 
        if len(os.listdir(src_dir_path)) > 0:    #check if directory contains files
            for file in os.listdir(src_dir_path):
                if file.endswith(src_file_ext):
                
                    #create file path
                    filepath = os.path.join(src_dir_path, file)
                
                    #read file content
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    #create markdown file by adding .md to existing filename with its original extension
                    new_filename = file + '.md'
                    dest_filepath = os.path.join(dest_dir_path, new_filename)

                    #write wrapped content
                    with open(dest_filepath, 'w', encoding='utf-8') as f:
                        f.write('```\n' + content + '\n```')
    
    except FileNotFoundError:
        print(f'Directory not found: {src_dir_path}')