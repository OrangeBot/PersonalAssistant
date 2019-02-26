from pyutils import fix_path


if __name__ == '__main__':
    for p in ['test', './test', '~/test']:
        print(p, fix_path(p))

