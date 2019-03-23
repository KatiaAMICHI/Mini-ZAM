from src.minizam.vm.vm import MiniZamVM
import sys

if __name__ == '__main__':
    vm = MiniZamVM()
    # arg = sys.argv[1]
    arg = r'/home/katy/PycharmProjects/Mini-ZAM/tests/rec_funs/facto.txt'
    vm.load_file(arg)
    vm.run()
