import gc


def render(filename, context, content_iterator=None):
    gc.collect()
    with open(filename, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break

            if content_iterator is not None and '{% content %}' in line:
                for content_line in content_iterator:
                    yield content_line
            else:
                try:
                    yield line.format(**context)
                except Exception as e:
                    yield 'ERROR: %r' % e

    gc.collect()
