# regression test for #1765
class Foo:
    def foo(self):
        if True:
            content_ids: Mapping[
                str, Optional[ContentId]
            ] = self.publisher_content_store.store_config_contents(files)


# regression test for #3685
query: Final[
    str
] = """
  SELECT my_column
  FROM my_table
  WHERE my_column > 1;
"""

# output

# regression test for #1765
class Foo:
    def foo(self):
        if True:
            content_ids: Mapping[str, Optional[ContentId]] = (
                self.publisher_content_store.store_config_contents(files)
            )


# regression test for #3685
query: Final[str] = """
  SELECT my_column
  FROM my_table
  WHERE my_column > 1;
"""
