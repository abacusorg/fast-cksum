import contexttimer


class ContextTimer(contexttimer.Timer):
    """
    A simple extension to the contexttimer lib that adds
    the `cumulative` keyword arg.

    TODO: rewrite
    """

    def __init__(self, *args, cumulative=False, **kwargs):
        self.cumulative = cumulative
        self.cumulative_time = 0.0  # all the time before the most recent/current loop
        args = list(args)
        if len(args) > 0:
            kwargs['prefix'] = args.pop(0)

        kwargs['fmt'] = kwargs.get('fmt', 'time: {:.2f} seconds')

        super(ContextTimer, self).__init__(*args, **kwargs)

    def __enter__(self):
        if self.cumulative and self.end:
            # The time from the most recent loop gets added to the cumulative time
            self.cumulative_time += self.end - self.start
        return super(ContextTimer, self).__enter__()

    @property
    def elapsed(self):
        if hasattr(self, 'start'):
            last_time = super(ContextTimer, self).elapsed
        else:
            last_time = 0.0
        return self.cumulative_time * self.factor + last_time

    def Start(self):
        self.__enter__()

    def stop(self, report=True):
        _output = self.output
        self.output = report
        self.__exit__(None, None, None)
        self.output = _output

    def report(self):
        print(' '.join([self.prefix, self.fmt.format(self.elapsed)]))
