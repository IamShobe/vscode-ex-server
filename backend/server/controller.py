from collections import defaultdict


def count(exts):
    counts = defaultdict(int)
    for ext in exts:
        for cat in ext.categories:
            counts[cat] += 1

    to_ret = []
    for key, value in counts.items():
        to_ret.append({
            "name": key,
            "count": value
        })

    return to_ret
