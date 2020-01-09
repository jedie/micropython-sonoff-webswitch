import gc

import uos


def render(filename, context, content_iterator=None):

    try:
        uos.stat(filename)  # Check if file exists
    except OSError:
        yield 'Error file not found: %r' % filename
        return

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
