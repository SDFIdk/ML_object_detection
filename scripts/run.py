"""
> Module-level docstring

Runner for the experiment, transient task, prototype.

"""

import sys
import json

from geometry import brahmagupta


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit

    if not len(args) == 4:
        raise SystemExit(f'Too many or too few side lengths given: {args=}')

    try:
        a, b, c, d = [float(side) for side in args]
    except Exception as e:
        raise SystemExit('Bad input')
    area = brahmagupta(a, b, c, d)

    result = dict(
        sides=dict(a=a, b=b, c=c, d=d),
        area=area,
    )
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
