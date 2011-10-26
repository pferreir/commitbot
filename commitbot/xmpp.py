import re

from twisted.words.xish import domish
from wokkel.subprotocols import XMPPHandler
from wokkel.xmppim import AvailablePresence, Presence


HTML_RE = re.compile('<[^<]+?>')


NS_MUC = 'http://jabber.org/protocol/muc'
NS_XHTML_IM = 'http://jabber.org/protocol/xhtml-im'
NS_XHTML_W3C = 'http://www.w3.org/1999/xhtml'


class CommitBot(XMPPHandler):

    def __init__(self, config):
        super(CommitBot, self).__init__()
        self.config = config

    def connectionMade(self):
        self.send(AvailablePresence())

        # join room
        pres = Presence()
        pres['to'] = self.config.room + '/' + self.config.nick
        x = pres.addElement((NS_MUC, 'x'))
        if not self.config.room_password is None:
            x.addElement('password', content = self.config.room_password)
        self.send(pres)

    def notify(self, data):
        # build the messages
        text = []
        html = []

        _html = self.config.format['notification'].format(**data)
        html.append(_html)
        text.append(HTML_RE.sub('', _html))

        html.append('<ul>')
        for c in data['commits']:
            c['title'] = c['message'].split('\n')[0]
            _html = self.config.format['commit'].format(**c)
            html.append(_html)
            text.append(HTML_RE.sub('', _html))
        html.append('</ul>')

        msg = domish.Element((None, 'message'))
        msg['to'] = self.config.room
        msg['type'] = 'groupchat'
        msg.addElement('body', content='\n'.join(text))
        wrap = msg.addElement((NS_XHTML_IM, 'html'))
        body = wrap.addElement((NS_XHTML_W3C, 'body'))
        body.addRawXml(''.join(html))

        self.send(msg)


