#!/usr/bin/python3

import os
import sys
import stat
import btrfs
from graphviz import Digraph

if len(sys.argv) < 2:
    print("Usage: {} <path>".format(sys.argv[0]))
    sys.exit(1)

G = Digraph(format='png')
G.attr('node', shape='plaintext')

file_node = '<<table border="0" cellborder="1" cellspacing="0"> <tr>'
extents = {}

# get EXTENT_DATA from file tree
fs = btrfs.FileSystem(sys.argv[1])
subvolid = btrfs.ioctl.ino_lookup(fs.fd).treeid
ino = os.stat(fs.fd).st_ino

i = 0
j = 0
total_len = 0
min_key = btrfs.ctree.Key(ino, btrfs.ctree.EXTENT_DATA_KEY, 0)
max_key = btrfs.ctree.Key(ino, btrfs.ctree.EXTENT_DATA_KEY, btrfs.ctree.ULLONG_MAX) - 1
for header, data in btrfs.ioctl.search_v2(fs.fd, subvolid, min_key, max_key):
    extent_data = btrfs.ctree.FileExtentItem(header, data)
    print(extent_data)

    if extent_data.type == btrfs.ctree.FILE_EXTENT_INLINE:
        print("nothing to print for inline extent")
        sys.exit(0)

    file_node += '<td port="{}"> addr: {}<br/> len: {}<br/> (offset: {})</td>'.format(
            "f"+str(i), extent_data.logical_offset,
            extent_data.num_bytes, extent_data.offset)
    total_len += extent_data.num_bytes

    if not extent_data.disk_bytenr in extents:
        # get EXTENT_ITEM from extent tree
        min_key = btrfs.ctree.Key(extent_data.disk_bytenr,
                btrfs.ctree.EXTENT_ITEM_KEY, extent_data.disk_num_bytes)
        max_key = btrfs.ctree.Key(extent_data.disk_bytenr,
                btrfs.ctree.EXTENT_ITEM_KEY, extent_data.disk_num_bytes)
        for header, data in btrfs.ioctl.search_v2(fs.fd, btrfs.ctree.EXTENT_TREE_OBJECTID, min_key, max_key, nr_items=1):
            extent_item = btrfs.ctree.ExtentItem(header, data)
            print(extent_item)
            extent_node = '<<table border="0" cellborder="1" cellspacing="0"> <tr>'
            extent_node += '<td port="e1"> vaddr: {}<br/> len: {}<br/> compression: {}</td>'.format(
                    extent_item.vaddr, extent_item.length, extent_data.compression_str)
            extent_node += '</tr></table>>'

            G.node('e'+str(j), extent_node)
            G.edge('file:f'+str(i), 'e'+str(j)+':e1')
            extents[extent_data.disk_bytenr] = j
            j += 1
    else:
        pos = extents[extent_data.disk_bytenr]
        G.edge('file:f'+str(i), 'e'+str(pos)+':e1')

    i += 1

file_node += '</tr></table>>'
label = '{} file extents point to {} extents (total len:{})'.format(
        i, j, total_len)
G.attr(label=label, labelloc='top')
G.node('file', file_node)
G.render('extent-info')
