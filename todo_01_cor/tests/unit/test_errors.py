from src.utils.errors import ParseError, ServiceError, StorageError


def test_error_classes_inheritance():
    pe = ParseError("bad date")
    assert isinstance(pe, Exception)

    se = ServiceError("geocode fail")
    assert isinstance(se, Exception)

    st = StorageError("io fail", path="/tmp/foo")
    assert isinstance(st, Exception)
    assert st.path == "/tmp/foo"
