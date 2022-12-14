some_dict = {
    "something_something":
        r"Lorem ipsum dolor sit amet, an sed convenire eloquentiam \t"
        r"signiferumque, duo ea vocibus consetetur scriptorem. Facer \t"
        r"signiferumque, duo ea vocibus consetetur scriptorem. Facer \t",
}

my_dict = {
    'a key in my dict': deformation_rupture_mean * constraint_rupture_something_str / 100.0
}

new_cache = {
    **cache,
    **{str(src.resolve()): get_cache_info(src) for src in sources},
}


# output


some_dict = {
    "something_something": (
        r"Lorem ipsum dolor sit amet, an sed convenire eloquentiam \t"
        r"signiferumque, duo ea vocibus consetetur scriptorem. Facer \t"
        r"signiferumque, duo ea vocibus consetetur scriptorem. Facer \t"
    ),
}

my_dict = {
    "a key in my dict": (
        deformation_rupture_mean * constraint_rupture_something_str / 100.0
    )
}

new_cache = {
    **cache,
    **{str(src.resolve()): get_cache_info(src) for src in sources},
}
