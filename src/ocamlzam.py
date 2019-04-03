from src.minizam.vm.vm import MiniZamVM
import sys
import os
import click
import time

if __name__ == '__main__':
    vm = MiniZamVM()
    if sys.argv[1] == "-o":
        vm.load_file_optimized(sys.argv[2])
        vm.run()
    else:
        vm.load_file(sys.argv[1])
        vm.run()
