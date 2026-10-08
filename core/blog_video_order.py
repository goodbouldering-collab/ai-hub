"""Move leading article videos without serializing or rewriting other markup."""
from html.parser import HTMLParser


class Spans(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.lines = [0]
        for line in source.splitlines(keepends=True):
            self.lines.append(self.lines[-1] + len(line))
        self.stack, self.nodes = [], []
        self.feed(source)

    def position_offset(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        node = dict(tag=tag, attrs=dict(attrs), start=self.position_offset(),
                    parent=self.stack[-1] if self.stack else None)
        self.nodes.append(node)
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]['tag'] == tag:
                node = self.stack[i]
                node['close'] = self.position_offset()
                node['end'] = self.source.index('>', node['close']) + 1
                del self.stack[i:]
                break


def move_leading_videos(source):
    parsed = Spans(source)
    containers = [n for n in parsed.nodes if 'content-wrap' in n['attrs'].get('class', '').split()]
    if len(containers) != 1:
        return source
    container = containers[0]
    children = [n for n in parsed.nodes if n['parent'] is container]
    heading = next((n['start'] for n in children if n['tag'] == 'h2'), container['close'])
    ranges = []
    for child in children:
        if child['start'] >= heading or 'end' not in child:
            continue
        raw = source[child['start']:child['end']]
        if child['tag'] not in {'figure','div','video'} or '<video' not in raw:
            continue
        start, end = child['start'], child['end']
        index = children.index(child)
        if index and children[index - 1]['tag'] == 'p':
            previous = children[index - 1]
            if 'まずは約49秒の動画で、結論をつかんでください。' in source[previous['start']:previous['end']]:
                start = previous['start']
        if index + 1 < len(children) and children[index + 1]['tag'] == 'script':
            following = children[index + 1]
            if 'data-fullscreen-on-play' in source[following['start']:following['end']]:
                end = following['end']
        ranges.append((start, end))
    if not ranges:
        return source
    video = ''.join(source[a:b] for a, b in ranges)
    result = source[:container['close']] + video + source[container['close']:]
    for start, end in reversed(ranges):
        result = result[:start] + result[end:]
    return result

