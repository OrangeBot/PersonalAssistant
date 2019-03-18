from pyutils import dump, load


def dump_protos(protos, path, engine=None):
    dump(what=[p.SerializeToString() for p in protos], where=path, engine=engine)


def load_protos(path, proto, engine=None):
    return [proto.FromString(bytes(p)) for p in load(where_from=path, engine=engine)]
