from html.parser import HTMLParser


class LinkParser(HTMLParser):

    def reset(self):
        HTMLParser.reset(self)
        self.links = []

    def handle_startag(self, tag, attrs):
        if tag == "a":
            attrs = dict(attrs)
            self.links.append(attrs["href"])
