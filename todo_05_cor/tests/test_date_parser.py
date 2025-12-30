def test_date_parser_importable():
    from src.services import date_parser
    assert hasattr(date_parser, 'parse_natural_date_iso')
