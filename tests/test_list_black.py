from black import FileMode, format_str


def test_list_concatenation_multiline():
    source = '''
search_fields = ["file__%s" % field for field in FileAdmin.search_fields] + [
    "resource__%s" % field for field in ResourceAdmin.search_fields
]
'''.lstrip()
    expected = '''
search_fields = (
    ["file__%s" % field for field in FileAdmin.search_fields]
    + ["resource__%s" % field for field in ResourceAdmin.search_fields]
)
'''.lstrip()
    assert format_str(source, mode=FileMode()) == expected

def test_list_concatenation_is_idempotent():
    source = '''
search_fields = ["file__%s" % field for field in FileAdmin.search_fields] + [
    "resource__%s" % field for field in ResourceAdmin.search_fields
]
'''.lstrip()
    once = format_str(source, mode=FileMode())
    twice = format_str(once, mode=FileMode())
    assert once == twice
