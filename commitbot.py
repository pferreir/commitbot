from twisted.python import log
from twisted.web import resource
from twisted.words.xish import domish
from wokkel.subprotocols import XMPPHandler
from wokkel.xmppim import AvailablePresence, Presence

import re
import json


NS_MUC = 'http://jabber.org/protocol/muc'
NS_XHTML_IM = 'http://jabber.org/protocol/xhtml-im'
NS_XHTML_W3C = 'http://www.w3.org/1999/xhtml'


HTML_RE = re.compile('<[^<]+?>')


STANDARD_FORMAT = {
    'notification': '<h1><span style="font-weight: bold;">New commits in <a href="{repository[url]}" name="{repository[name]}">{repository[name]}</a> ({ref})<br/></span></h1>',
    'commit': '<li><a href="{url}" name="{id}">{id:.8}</a>: {title:.50} | <em>{author[name]}</em><br/></li>'
    }


class CommitBot(XMPPHandler):

    def __init__(self, room, nick, password=None, format=STANDARD_FORMAT):
        XMPPHandler.__init__(self)

        self.room = room
        self.nick = nick
        self.password = password
        self.format = format

    def connectionMade(self):
        self.send(AvailablePresence())

        # add handlers

        # join room
        pres = Presence()
        pres['to'] = self.room + '/' + self.nick
        x = pres.addElement((NS_MUC, 'x'))
        if not self.password is None:
            x.addElement('password', content = self.password)
        self.send(pres)

    def notify(self, data):
        # build the messages
        text = []
        html = []

        _html = self.format['notification'].format(**data)
        html.append(_html)
        text.append(HTML_RE.sub('', _html))

        html.append('<ul>')
        for c in data['commits']:
            c['title'] = c['message'].split('\n')[0]
            _html = self.format['commit'].format(**c)
            html.append(_html)
            text.append(HTML_RE.sub('', _html))
        html.append('</ul>')

        msg = domish.Element((None, 'message'))
        msg['to'] = self.room
        msg['type'] = 'groupchat'
        msg.addElement('body', content='\n'.join(text))
        wrap = msg.addElement((NS_XHTML_IM, 'html'))
        body = wrap.addElement((NS_XHTML_W3C, 'body'))
        body.addRawXml(''.join(html))

        self.send(msg)


class WebHook(resource.Resource):
    isLeaf = True

    def __init__(self, bot):
        resource.Resource.__init__(self)
        self.bot = bot

    def render_GET(self, req):
        return "commitbot ready to rock!"

    def render_POST(self, req):
        data = json.loads(req.args['payload'][0])
        self.bot.notify(data)
        return ""
