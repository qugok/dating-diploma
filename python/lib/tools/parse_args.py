import argparse

def congifure_parser():
    parser = argparse.ArgumentParser(prog='Media Server')
    parser.add_argument('-c', '--config-folder')
    parser.add_argument('-l', '--log-path')
    parser.add_argument('-p', '--port')

    return parser
