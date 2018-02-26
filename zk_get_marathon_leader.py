from kazoo.client import KazooClient
import sys
zk = KazooClient(hosts='127.0.0.1:2181')
zk.start()
leaders_unsort = zk.get_children('/marathon/leader/')
leaders = sorted(leaders_unsort)
# leaders = leaders_unsort
# print leaders
# print len(leaders)
leader=zk.get('/marathon/leader/'+leaders[0])
print leader[0][:-5]
zk.stop()
