#!/usr/bin/python3

import os
import sys
import stat
import btrfs
from graphviz import Digraph

if len(sys.argv) < 2:
    print("Usage: {} <mnt>".format(sys.argv[0]))
    sys.exit(1)

G = Digraph(format='png')
G.attr('node', shape='circle', fixedsize='true')
G.attr(rankdir='BT')

fs = btrfs.FileSystem(sys.argv[1])

# add node
min_key = btrfs.ctree.Key(0, btrfs.ctree.QGROUP_INFO_KEY, 0)
max_key = btrfs.ctree.Key(0, btrfs.ctree.QGROUP_INFO_KEY, btrfs.ctree.ULLONG_MAX) - 1
for header, data in btrfs.ioctl.search_v2(fs.fd, btrfs.ctree.QUOTA_TREE_OBJECTID, min_key, max_key):
    cluster = 'cluster' + str(btrfs.ctree.qgroup_level(header.offset))
    qgroupid = btrfs.ctree.key_objectid_str(header.offset, btrfs.ctree.QGROUP_RELATION_KEY)

    print(qgroupid)
    with G.subgraph(name=cluster) as c:
        c.node(qgroupid, qgroupid, {'rank': 'same'})

# add edge
min_key = btrfs.ctree.Key(0, btrfs.ctree.QGROUP_RELATION_KEY, 0)
max_key = btrfs.ctree.Key(btrfs.ctree.ULLONG_MAX, btrfs.ctree.QGROUP_RELATION_KEY, btrfs.ctree.ULLONG_MAX) - 1
for header, data in btrfs.ioctl.search_v2(fs.fd, btrfs.ctree.QUOTA_TREE_OBJECTID, min_key, max_key):
    if header.objectid > header.offset:
        continue

    child = btrfs.ctree.key_objectid_str(header.objectid, btrfs.ctree.QGROUP_RELATION_KEY)
    parent = btrfs.ctree.key_objectid_str(header.offset, btrfs.ctree.QGROUP_RELATION_KEY)

    print(child, parent)
    G.edge(child, parent)

G.render('qgroup-relation')
