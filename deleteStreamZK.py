#!/usr/bin/env python

from kazoo.client import KazooClient
import sys
zk = KazooClient(hosts='127.0.0.1:2181')
zk.start()
print sys.argv[1]
path = "/vos-apps/sample_stream_processing_engine/v1/stream_processing/" + sys.argv[1]
print path
zk.delete(path, recursive=True)
zk.stop()
