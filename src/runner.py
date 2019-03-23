from src.minizam.vm.vm import MiniZamVM
import sys
import os

PATH_dec = "/home/katy/PycharmProjects/Mini-ZAM/tests/block_values/"


def run_main():
    for file in os.listdir(PATH_dec):
        vm = MiniZamVM()
        arg = str(PATH_dec+file)
        print("arg: ", arg)
        vm.load_file(arg)
        vm.run()


if __name__ == '__main__':
    vm = MiniZamVM()
    arg = PATH_dec + "array_set.txt"
    print("arg: ", arg)
    vm.load_file(arg)
    vm.run()
