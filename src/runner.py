from minizam.vm.vm import MiniZamVM
import sys
if __name__ == '__main__':
    vm = MiniZamVM()
    vm.load_file(sys.argv[1])
    vm.run()
