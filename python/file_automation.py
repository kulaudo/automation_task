#!/usr/bin/env python
import sys
import os
import shutil
import logging
import collections
from datetime import datetime
from enum import Enum, auto

logging.basicConfig(filename='debug.log',level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

def valid_operations():
    return {"cp","mv","rm","ftp","email"}

def read_config(config,sep='|'):
    logging.info('read_config: config={}, sep={}'.format(config,sep))

    parsed_op = []
    if not check_exists(config):
        print ("{} not exists".format(config))
        exit(1)
    check_valid_file(config,sep)
    
    with open(config, 'r') as f:
        lines = f.readlines()
        for line in lines:
            d = dict()
            d['src'], d['dst'], d['option'], d['type'] = line.rstrip().split(sep)
            parsed_op.append(d)
    return parsed_op

def check_valid_file(config,sep):
    logging.debug('check_valid_file: config={}, sep={}'.format(config,sep))
    if not os.path.isfile(config) or os.path.splitext(config)[1] not in ('.cfg','.config'):
        print ("ERROR: Not valid filename {}, should be .cfg or .config".format(config))
        exit(1)
    with open(config, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if collections.Counter(line)[sep] != 3:
                print ("Invalid File Format: sep count should be 3, line: {}".format(line))
                exit(1)
            op = line.replace('\n','').split(sep)[3]
            if op not in valid_operations():
                print ("Invalid File Operations: {}, line: {}".format(op, line))
                exit(1)
    logging.debug('check_valid_file: success')


def merge_path(path1, path2):
    logging.info('merge_path: path1={}, path2={}'.format(path1,path2))
    pieces = []
    parts1, tail1 = os.path.splitdrive(path1)
    parts2, tail2 = os.path.splitdrive(path2)
    result = path2
    parts1 = tail1.split('\\') if '\\' in tail1 else tail1.split('/')
    parts2 = tail2.split('\\') if '\\' in tail2 else tail2.split('/')
    
    for pitem in parts1:
        if pitem != '' and pitem not in parts2:
            pieces.append(pitem)    
    for piece in pieces:
        result = os.path.join(result, piece)
    logging.info('merge_path result: {}'.format(result))
    return result


def do_cfg_action(action: dict):
    logging.debug("cfg action: {}".format(action))

    
    if action['type'] == 'rm':
        print (shutil.rmtree(action['src']))
    else:
        if os.path.isfile(action['src']):
            cmd_file(action['src'], action['dst'], action['type'], action['option'])
        cmd_folder(action['src'], action['dst'], action['type'], action['option'])

# def processed_path(path):
#     drive, tail = os.path.splitdrive(path)
    
#     # tail = tail.split('\\') if '\\' in tail else tail.split('/')
#     # print("*tail=",*tail, "tail=",tail)
#     result = os.path.join(drive,*tail)
#     print (os.path.exists(path))
#     print (path)
#     return result

    

def cmd_folder(src:str, dst:str, type:str, option:str):
    logging.debug ("cmd_folder: source:{}, dst:{}, type:{}, option:{}".format(src, repr(dst), type, option))
    print(os.path.exists(src))
    print(os.listdir(dst))
    for folder, subfolder, filename in os.walk(src):
        print(folder, subfolder, filename)
        cmd_folder_core(folder, dst, type, subfolder, filename, option)


def cmd_folder_core(folder, dst, type, subfolder, filename, option):
    print ('Processing folder: {}'.format(folder))
    cmd_subfolder(folder, subfolder, dst, type, option)
    cmd_files(folder, dst, type, filename, option)


def cmd_subfolder(folder, subfolder, dst, type, option):
    for sf in subfolder:
        print ('Processing subfolder: {}'.format(sf))
        #cmd_subfolder(subfolder, subfolder, dst, type, option)
        # cmd_files(folder, dst, type, filename, option)

def cmd_file(filepath, dst, tp, option=None):
    merge_path(filepath,dst)
    if tp == "cp":
        file_copy(filepath, dst)
    elif tp == "mv":
        file_move(filepath, dst)
    elif tp == "rm":
        file_delete(filepath)

def cmd_files(folder, dst, tp, files, option):
    for filename in files:
        filepath = os.path.join(folder, filename)
        cmd_file(filepath, dst, tp, option)


def get_now_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def check_exists(path):
    if not os.path.exists(path):
        logging.error("{} not exists".format(path))
        return False
    return True

def file_copy(filepath, dst):
    #d = merge_path(folder, dst)
    try:
        if not os.path.exists(dst):
            os.mkdir(dst)
        shutil.copy(filepath, dst)
        logging.info('Copied file: {}'.format(filepath))
    except IOError as e:
        logging.error('copying file: {} with exception {}'.format(
            filepath, e))


def file_move(filepath, dst):    
    logging.info('file_move: file={}, dst={}'.format(filepath,dst))
    for p in filepath, dst:
        if not check_exists(p):
            return
    try:
        shutil.move(filepath, dst)
        logging.info('Moved file: {}'.format(filepath))
    except IOError as e:
        logging.error('moving file: {} with exception {}'.format(
            filepath, e))


def file_delete(filepath):
    logging.info('file_delete: file={}'.format(filepath))
    try:
        os.unlink(filepath)
        logging.info('Deleted file: {}'.format(filepath))
    except IOError as e:
        logging.error('deleting file: {} with exception {}'.format(
            filepath, e))

def main():
    if len(sys.argv) == 2:        
        for action in read_config(sys.argv[1]):
            print (action)
            do_cfg_action(action)
    else:
        a = input("file name:")
        if not a:
            print ("usage: ./file_automation.py [config_file path]")
        else:
            for action in read_config(a):
                print (action)
                do_cfg_action(action)

if __name__ == "__main__":
    main()
