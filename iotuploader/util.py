import re
import sys

def make_safe_path(orig):
    return re.sub(r'[^0-9,a-z,A-Z,-]', '_', orig)

if __name__ == "__main__":
    print(sys.argv[1])
    print(make_safe_path(sys.argv[1]))

