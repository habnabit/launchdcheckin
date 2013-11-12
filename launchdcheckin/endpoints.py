# Copyright (c) Aaron Gallagher <_@habnab.it>
# See COPYING for details.

import os
import socket

from twisted.internet.endpoints import AdoptedStreamServerEndpoint
from twisted.internet.error import AlreadyListened
from twisted.internet.interfaces import IStreamServerEndpoint, IStreamServerEndpointStringParser
from twisted.internet import defer, fdesc
from twisted.plugin import IPlugin
from zope.interface import implementer

from launchdcheckin._impl import LaunchData
from launchdcheckin._unix import Port


@implementer(IStreamServerEndpoint)
class LaunchdUNIXEndpoint(object):
    def __init__(self, reactor, fileno):
        self.reactor = reactor
        self.fileno = fileno
        self._used = False

    def listen(self, factory):
        if self._used:
            return defer.fail(AlreadyListened())
        self._used = True

        try:
            fdesc.setNonBlocking(self.fileno)
            port = Port._fromListeningDescriptor(
                self.reactor, self.fileno, factory)
            port.startListening()
            os.close(self.fileno)
        except:
            return defer.fail()
        return defer.succeed(port)


@implementer(IPlugin, IStreamServerEndpointStringParser)
class LaunchdParser(object):
    prefix = 'launchd'

    def parseStreamServer(self, reactor, domain, *indices):
        checkin = LaunchData.from_string('CheckIn')
        sock = checkin.msg()['Sockets']
        for index in indices:
            if index.isdigit():
                index = int(index)
            sock = sock[index]
        if sock.type != 'fd':
            raise ValueError('socket at %r is of the wrong type (%r)' % (indices, sock.type))
        if domain == 'UNIX':
            return LaunchdUNIXEndpoint(reactor, sock.data)
        addressFamily = getattr(socket, 'AF_' + domain)
        return AdoptedStreamServerEndpoint(reactor, sock.data, addressFamily)
