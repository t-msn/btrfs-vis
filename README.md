# Overview
visualize some btrfs internal by using [graphviz](https://www.graphviz.org/)
and [python-btrfs](https://github.com/knorrie/python-btrfs).

License: GPLv2

# Example
```./extent-info.py <path/to/file>```

![extent-info](https://github.com/t-msn/btrfs-vis/blob/master/example/extent-info.png)

tip: "btrfs inspect-internal logical-resolve \<vaddr\>" will list all the files which points the block of given \<vaddr\>

---

```./qgroup-relation.py <path/to/mountpoint>```

![qgroup-relation](https://github.com/t-msn/btrfs-vis/blob/master/example/qgroup-relation.png)
