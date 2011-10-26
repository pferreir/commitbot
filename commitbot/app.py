# -*- mode: python -*-

import argparse
import json

from twisted.application import service, internet, app
from twisted.web import server
from twisted.words.protocols.jabber import jid
from twisted.internet import reactor
from wokkel.client import XMPPClient
from wokkel.ping import PingHandler

from commitbot.web import WebHook
from commitbot.xmpp import CommitBot


def load_config(args):
    with open(args.config_file, 'r') as f:
        data = json.load(f)
    return argparse.Namespace(**data)


def start_services(config):
    client = XMPPClient(jid.internJID(config.credentials['jid']), config.credentials['password'])

    application = service.Application('commitbot')

    bot = CommitBot(config)
    bot.setHandlerParent(client)

    site = server.Site(WebHook(config, bot))
    tcp_server = reactor.listenTCP(8888, site)

    app.startApplication(application, None)
    client.startService()

    reactor.run()

def main():
    parser = argparse.ArgumentParser(description='CommitBot')
    parser.add_argument('config_file')
    args = parser.parse_args()

    config = load_config(args)
    start_services(config)
