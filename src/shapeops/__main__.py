from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals

import sys
import json
import shapeops


def main():
    data = json.load(sys.stdin)

    if {'--profile'}.intersection(sys.argv):
        import cProfile

        ret = []
        cProfile.runctx(
            'ret.append(shapeops.union(data))',
            globals={'shapeops': shapeops},
            locals={'data': data, 'ret': ret},
            sort="cumtime",
            filename="shapeops.cprof")
        result = ret[0]
    else:
        result = shapeops.union(data)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
