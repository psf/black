# flags: --unstable
self._edits.append(
    {"operation": "update", "id": index, "fields": list(fields), "region_fields": []}
)
very_long_function_name_for_a_call_with_a_single_collection_argument([first, second, third])
very_long_function_name_for_a_call_with_a_single_collection_argument({first, second, third})
very_long_function_name_for_a_call_with_a_single_collection_argument((first, second, third))
very_long_function_name_for_a_call_with_a_single_collection_argument(*[first, second, third])
very_long_function_name_for_a_call_with_a_single_collection_argument(**{"first": first})
short_call([first, second])
very_long_function_name_for_a_call_with_a_single_collection_argument(
    [first, second, third],
)
very_long_function_name_for_a_call_with_a_single_collection_argument(
    [first, second, third], other
)

# output
self._edits.append({
    "operation": "update", "id": index, "fields": list(fields), "region_fields": []
})
very_long_function_name_for_a_call_with_a_single_collection_argument([
    first, second, third
])
very_long_function_name_for_a_call_with_a_single_collection_argument({
    first, second, third
})
very_long_function_name_for_a_call_with_a_single_collection_argument((
    first, second, third
))
very_long_function_name_for_a_call_with_a_single_collection_argument(*[
    first, second, third
])
very_long_function_name_for_a_call_with_a_single_collection_argument(**{"first": first})
short_call([first, second])
very_long_function_name_for_a_call_with_a_single_collection_argument(
    [first, second, third],
)
very_long_function_name_for_a_call_with_a_single_collection_argument(
    [first, second, third], other
)
