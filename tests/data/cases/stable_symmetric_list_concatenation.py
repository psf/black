# Stable style must keep the existing asymmetric bracket split.
search_fields = ["file__%s" % field for field in FileAdmin.search_fields] + [
    "resource__%s" % field for field in ResourceAdmin.search_fields
]
