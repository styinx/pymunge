from util.logging import Ansi
from util.time import measure, duration


class Statistic:

    class Tag:
        Parse = 'parse'
        Build = 'build'

    def __init__(self):
        self.times = {
            'parse': {},
            'build': {}
        }

    def record(self, tag: str, name: str, f: callable, *args, **kwargs):
        time, result = measure(f, *args, **kwargs)

        if tag not in self.times:
            self.times[tag] = {}

        self.times[tag][name] = time

        return result

    def summary(self):
        parse_time = duration(sum(x for x in self.times['parse'].values()))
        build_time = duration(sum(x for x in self.times['build'].values()))
        string_len = len(max(parse_time, build_time))

        s = Ansi.color_fg(Ansi.GreenForeground, 'Statistic Summary: \n')
        s += Ansi.color_fg(Ansi.CyanForeground, f'  Parse time: {parse_time:>{string_len}s}\n')
        s += Ansi.color_fg(Ansi.CyanForeground, f'  Build time: {build_time:>{string_len}s}\n')
        print(s)
