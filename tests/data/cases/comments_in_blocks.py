# Test cases from:
# - https://github.com/psf/black/issues/1798
# - https://github.com/psf/black/issues/1499
# - https://github.com/psf/black/issues/1211
# - https://github.com/psf/black/issues/563

(
    lambda
    # a comment
    : None
)

(
    lambda:
    # b comment
    None
)

(
    lambda
    # a comment
    :
    # b comment
    None
)

[
    x
    # Let's do this
    for
    # OK?
    x
    # Some comment
    # And another
    in
    # One more
    y
]

return [
    (offers[offer_index], 1.0)
    for offer_index, _
    # avoid returning any offers that don't match the grammar so
    # that the return values here are consistent with what would be
    # returned in AcceptValidHeader
    in self._parse_and_normalize_offers(offers)
]

from foo import (
    bar,
    # qux
)


def convert(collection):
    # replace all variables by integers
    replacement_dict = {
        variable: f"{index}"
        for index, variable
        # 0 is reserved as line terminator
        in enumerate(collection.variables(), start=1)
    }


{
    i: i
    for i
    # a comment
    in range(5)
}


def get_subtree_proof_nodes(
    chunk_index_groups: Sequence[Tuple[int, ...], ...],
) -> Tuple[int, ...]:
    subtree_node_paths = (
        # We take a candidate element from each group and shift it to
        # remove the bits that are not common to other group members, then
        # we convert it to a tree path that all elements from this group
        # have in common.
        chunk_index
        for chunk_index, bits_to_truncate
        # Each group will contain an even "power-of-two" number of# elements.
        # This tells us how many tailing bits each element has# which need to
        # be truncated to get the group's common prefix.
        in ((group[0], (len(group) - 1).bit_length()) for group in chunk_index_groups)
    )
    return subtree_node_paths


if (
    # comment1
    a
    # comment2
    or (
        # comment3
        (
            # comment4
            b
        )
        # comment5
        and
        # comment6
        c
        or (
            # comment7
            d
        )
    )
):
    print("Foo")
