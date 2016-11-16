from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals

import sys
import json
import shapeops


def main():
    data = json.load(sys.stdin)
    result = shapeops.union(data)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
