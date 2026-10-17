import io
import re

EPSILON = 0.004


def Hex(rgb):
    r, g, b = [max(0, min(255, int(round(v)))) for v in rgb]
    return "#%02x%02x%02x" % (r, g, b)


def Rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def Mix(a, b, t):
    ra, rb = Rgb(a), Rgb(b)
    return Hex([ra[i] + (rb[i] - ra[i]) * t for i in range(3)])


def FormatNumber(v):
    if isinstance(v, float):
        s = ("%.3f" % v).rstrip("0").rstrip(".")
        return s if s else "0"
    return str(v)


def Escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Node:
    def __init__(self, scene, tag, attrs, text=None):
        self.scene = scene
        self.tag = tag
        self.attrs = dict(attrs)
        self.text = text
        self.children = []
        self.tracks = {}
        self.discrete = set()

    def add(self, tag, text=None, **attrs):
        node = Node(self.scene, tag, {k.replace("_", "-"): v for k, v in attrs.items()}, text)
        self.children.append(node)
        return node

    def _track(self, attr):
        attr = attr.replace("_", "-")
        if attr not in self.tracks:
            v0 = self.attrs[attr]
            self.tracks[attr] = [(0.0, v0 if isinstance(v0, str) else FormatNumber(v0))]
        return attr, self.tracks[attr]

    def Set(self, t, attr, value):
        attr, track = self._track(attr)
        value = FormatNumber(value) if not isinstance(value, str) else value
        last_t, last_v = track[-1]
        if t < last_t - 1e-9:
            raise ValueError("time goes backwards: %s %s %.3f < %.3f" % (self.tag, attr, t, last_t))
        if value == last_v:
            return self
        if t - EPSILON > last_t:
            track.append((t - EPSILON, last_v))
        elif t <= last_t:
            track[-1] = (last_t, value)
            return self
        track.append((t, value))
        return self

    def Ramp(self, t0, t1, attr, value):
        attr, track = self._track(attr)
        value = FormatNumber(value) if not isinstance(value, str) else value
        last_t, last_v = track[-1]
        if t0 < last_t - 1e-9:
            raise ValueError("time goes backwards: %s %s" % (self.tag, attr))
        if t0 > last_t:
            track.append((t0, last_v))
        track.append((t1, value))
        return self

    def Steps(self, attr, items):
        attr = attr.replace("_", "-")
        v0 = self.attrs[attr]
        track = [(0.0, v0 if isinstance(v0, str) else FormatNumber(v0))]
        for t, v in items:
            if t < track[-1][0]:
                raise ValueError("time goes backwards: %s %s" % (self.tag, attr))
            track.append((t, v if isinstance(v, str) else FormatNumber(v)))
        self.tracks[attr] = track
        self.discrete.add(attr)
        return self

    def Show(self, t0, t1=None):
        self.Set(t0, "opacity", 1)
        if t1 is not None:
            self.Set(t1, "opacity", 0)
        return self

    def Value(self, attr, t):
        track = self.tracks.get(attr)
        if not track:
            return None
        if t <= track[0][0]:
            return track[0][1]
        if attr in self.discrete:
            value = track[0][1]
            for tt, vv in track:
                if tt <= t:
                    value = vv
            return value
        for i in range(1, len(track)):
            t0, v0 = track[i - 1]
            t1, v1 = track[i]
            if t <= t1:
                if v0 == v1 or t1 == t0:
                    return v1 if t >= t1 else v0
                f = (t - t0) / (t1 - t0)
                if v0.startswith("#") and v1.startswith("#") and len(v0) == 7 and len(v1) == 7:
                    return Mix(v0, v1, f)
                try:
                    return FormatNumber(float(v0) + (float(v1) - float(v0)) * f)
                except ValueError:
                    return v0
        return track[-1][1]

    def Snapshot(self, t):
        attrs = dict(self.attrs)
        for attr in self.tracks:
            attrs[attr] = self.Value(attr, t)
        attr_text = "".join(' %s="%s"' % (k, Escape(str(v))) for k, v in attrs.items())
        inner = "".join(c.Snapshot(t) for c in self.children)
        if self.text is not None:
            inner = Escape(self.text) + inner
        if inner == "":
            return "<%s%s/>" % (self.tag, attr_text)
        return "<%s%s>%s</%s>" % (self.tag, attr_text, inner, self.tag)

    def Render(self, total, indent=0):
        parts = []
        attr_text = "".join(' %s="%s"' % (k, Escape(str(v)) if k != "d" else v) for k, v in self.attrs.items())
        anims = []
        for attr, track in self.tracks.items():
            keys = list(track)
            is_discrete = attr in self.discrete
            if keys[0][0] > 0:
                keys.insert(0, (0.0, keys[0][1]))
            if keys[-1][0] < total and not is_discrete:
                keys.append((total, keys[-1][1]))
            if all(v == keys[0][1] for _, v in keys):
                continue
            times = []
            prev = -1.0
            for t, _ in keys:
                n = min(1.0, t / total)
                if n <= prev:
                    n = prev + 0.00001
                times.append(n)
                prev = n
            if not is_discrete:
                times[-1] = 1.0
                if len(times) > 1 and times[-2] >= 1.0:
                    times[-2] = 1.0 - 0.00001
            mode = ' calcMode="discrete"' if is_discrete else ""
            anims.append(
                '<animate attributeName="%s" dur="%ss" repeatCount="indefinite"%s keyTimes="%s" values="%s"/>'
                % (attr, FormatNumber(total), mode, ";".join("%.4f" % n for n in times), ";".join(v for _, v in keys))
            )
        inner = "".join(anims) + "".join(c.Render(total) for c in self.children)
        if self.text is not None:
            inner = Escape(self.text) + inner
        if inner == "":
            return "<%s%s/>\n" % (self.tag, attr_text)
        return "<%s%s>%s</%s>\n" % (self.tag, attr_text, inner, self.tag)


class Scene:
    def __init__(self, name, width, height, duration, hold, background="#ffffff", still=None):
        self.name = name
        self.width = width
        self.height = height
        self.duration = duration
        self.hold = hold
        self.total = duration + hold
        self.notes = []
        self.root = Node(self, "svg", {
            "class": "fig illust motion",
            "data-fig": name,
            "viewBox": "0 0 %d %d" % (width, height),
            "role": "img",
        })
        if still is not None:
            self.root.attrs["data-still"] = str(still)
        self.root.add("rect", x=0, y=0, width=width, height=height, rx=14, fill=background)

    def Note(self, t, who, text):
        self.notes.append((t, who, text))

    def Text(self, parent, x, y, text, size=16, weight=700, fill="#1f2937", anchor="start", **extra):
        style = "font-size:%spx;font-weight:%s;fill:%s" % (size, weight, fill)
        return parent.add("text", text=text, x=x, y=y, text_anchor=anchor, style=style, **extra)

    def TextStack(self, parent, x, y, items, size=16, weight=700, fill="#1f2937", anchor="start"):
        nodes = []
        for t0, t1, text in items:
            node = self.Text(parent, x, y, text, size, weight, fill, anchor, opacity=0)
            node.Show(t0, t1)
            nodes.append(node)
        return nodes

    def Counter(self, parent, x, y, series, size=24, fill="#1f2937", anchor="start", start_value=0):
        items = []
        points = [(0.0, start_value)] + list(series)
        for i, (t, v) in enumerate(points):
            t_end = points[i + 1][0] if i + 1 < len(points) else None
            items.append((t if i > 0 else 0.0, t_end, "{:,}".format(v)))
        nodes = []
        for i, (t0, t1, text) in enumerate(items):
            node = self.Text(parent, x, y, text, size, 700, fill, anchor, opacity=1 if i == 0 else 0)
            if i == 0:
                if t1 is not None:
                    node.Set(t1, "opacity", 0)
            else:
                node.Show(t0, t1)
            nodes.append(node)
        return nodes

    def Render(self):
        return self.root.Render(self.total)

    def SnapshotAt(self, t):
        return self.root.Snapshot(t)

    def Report(self):
        lines = ["time(s)  who         what"]
        for t, who, text in sorted(self.notes, key=lambda n: n[0]):
            lines.append("%6.2f   %-10s  %s" % (t, who, text))
        lines.append("total %.1fs = animation %.1fs + hold %.1fs" % (self.total, self.duration, self.hold))
        return "\n".join(lines)


def ReplaceBetween(path, begin, end, body):
    text = io.open(path, encoding="utf-8").read()
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.S)
    if not pattern.search(text):
        raise ValueError("marker not found")
    text = pattern.sub(lambda m: begin + "\n" + body + "\n" + end, text)
    io.open(path, "w", encoding="utf-8", newline="").write(text)
