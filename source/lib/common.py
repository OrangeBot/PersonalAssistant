from google.protobuf.text_format import Parse
from pyutils import dump, load, read


def dump_protos(protos, path, engine=None):
    dump(what=[p.SerializeToString() for p in protos], where=path, engine=engine)


def load_protos(path, proto, engine=None):
    return [proto.FromString(bytes(p)) for p in load(where_from=path, engine=engine)]


def load_config(path, proto):
    return Parse(read(path), proto())
