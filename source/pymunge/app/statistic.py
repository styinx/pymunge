from util.logging import Ansi
from util.time import measure, duration


class Statistic:

    class Tag:
        Parse = 'Parse'
        Build = 'Build'

    def __init__(self):
        self.times = {}

    def record(self, tag: str, name: str, f: callable, *args, **kwargs):
        time, result = measure(f, *args, **kwargs)

        if tag not in self.times:
            self.times[tag] = {}

        self.times[tag][name] = time

        return result

    def details(self):
        for tag, keys in self.times.items():
            times = self.times[tag]
            key_len = max(map(len, times.keys()))
            time_len = max(map(lambda x: len(duration(x, True)), times.values()))

            s = Ansi.color_fg(Ansi.GreenForeground, f'\nStatistic Details "{tag}": \n')
            for key, time in {k: duration(v, True) for k, v in sorted(times.items(), key=lambda x : x[1])}.items():
                s += Ansi.color_fg(Ansi.CyanForeground, f'  {key:<{key_len}s}: {time:>{time_len}s}\n')
            print(s)

    def summary(self):
        summed_times = {tag: duration(sum(x for x in keys.values()), True) for tag, keys in self.times.items()}

        tag_len = max(map(len, self.times.keys()))
        time_len = max(map(len, summed_times.values()))

        s = Ansi.color_fg(Ansi.GreenForeground, '\nStatistic Summary: \n')
        for tag, time in summed_times.items():
            s += Ansi.color_fg(Ansi.CyanForeground, f'  {tag:<{tag_len}s}: {time:>{time_len}s}\n')
        print(s)
