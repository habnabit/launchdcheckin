launchdcheckin
==============

Enough support for ``launchd(1)`` checkin to get listening sockets out, but not
much else. The primary purpose of this package is to provide a ``launchd``
endpoint type for Twisted. Given a ``launchd.plist`` that includes::

  <key>Sockets</key>
  <dict>
    <key>Listeners</key>
    <dict>
      <key>SecureSocketWithKey</key>
      <string>SOME_AGENT</string>
    </dict>
  </dict>

The endpoint description would be ``launchd:UNIX:Listeners:0``, because this is
a UNIX domain socket, and the socket key is ``Listeners``.
