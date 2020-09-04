#!/usr/bin/env python
import sys
import os
import shutil
from datetime import datetime


def read_config(config):
    parsed_op = []
    check_exists(config)
    if not os.path.isfile(config) and os.path.splitext(config)[1] in ('.cfg','.config'): 
        with open(config, 'r') as f:
            lines = f.readlines()
            for line in lines:
                d = dict()
                d['src'], d['dest'], d['options'], d['type'] = line.rstrip().split('|')
                parsed_op.append(d)
        return parsed_op


def merge_path(path1, path2):
    pieces = []
    parts1, tail1 = os.path.splitdrive(path1)
    parts2, tail2 = os.path.splitdrive(path2)
    result = path2
    parts1 = tail1.split('\\') if '\\' in tail1 else tail1.split('/')
    parts2 = tail2.split('\\') if '\\' in tail2 else tail2.split('/')
    
    for pitem in parts1:
        if pitem != '' and pitem not in parts2:
            pieces.append(pitem)
    print(result, pieces)
    for piece in pieces:
        result = os.path.join(result, piece)
    return result


def file_action(options):
    if len(options['type']) == 1:
        cmd_folder(options['src'], options['dest'], options['type'])
        if options['type'] == 'd':
            shutil.rmtree(options['src'])


def cmd_folder(source, dest, option):
    for folder, subfolder, filename in os.walk(source):
        cmd_folder_core(folder, dest, option, subfolder, filename)


def cmd_folder_core(folder, dest, option, subfolder, filename):
    print('Processing folder: {}'.format(folder))
    cmd_subfolder(folder, option, subfolder)
    cmd_files(folder, dest, option, filename)


def cmd_subfolder(folder, option, subfolder):
    for sf in subfolder:
        print('Processing subfolder: {}'.format(sf))


def cmd_files(folder, dest, option, files):
    for filename in files:
        fn = os.path.join(folder, filename)
        if option == 'c':
            file_copy(fn, folder, dest)
        if option == 'm':
            file_move(fn, folder, dest)
        if option == 'd':
            file_delete(fn, folder, dest)


def get_now_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def check_exists(path):
    if not os.path.exists(path):
        print("ERROR : {} not exists".format(path))
        exit(1)
    

def file_copy(filename, folder, dest):
    fn = os.path.join(folder, filename)
    #d = merge_path(folder, dest)
    try:
        if not os.path.exists(d):
            os.mkdir(d)
        shutil.copy(fn, d)
        print('[{}] Copied file: {}'.format(get_now_time(), fn))
    except IOError as e:
        print('ERROR copying file: {} in {} with exception {}'.format(
            filename, folder, e))


def file_move(filename, folder, dest):
    fn = os.path.join(folder, filename)
    #d = merge_path(folder, dest)
    for p in filename, folder,dest:
        if not check_exists(p):
            exit(1)
    try:

        shutil.move(fn, dest)
        print('[{}] Moved file: {}'.format(get_now_time(), fn))
    except IOError as e:
        print('ERROR moving file: {} in {} with exception {}'.format(
            filename, folder, e))


def file_delete(filename, folder, dest):
    fn = os.path.join(folder, filename)
    try:
        os.unlink(filename)
        print('[{}] Deleted file: {}'.format(get_now_time(), fn))
    except IOError as e:
        print('ERROR deleting file: {} in {} with exception {}'.format(
            filename, folder, e))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        print(read_config(sys.argv[1]))
        for op in read_config(sys.argv[1]):
            print(op)
            
    else:
        print("usage: ./file_automation.py config_file.cfg/.config ")
