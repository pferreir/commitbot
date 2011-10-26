import json
from twisted.web import resource


class WebHook(resource.Resource):
    isLeaf = True

    def __init__(self, config, bot):
        resource.Resource.__init__(self)
        self.bot = bot
        self.config = config

    def render_GET(self, req):
        return "commitbot ready to rock!"

    def render_POST(self, req):
        data = json.loads(req.args['payload'][0])
        self.bot.notify(data)
        return ""
