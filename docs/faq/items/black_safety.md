# Is Black safe to use?

Yes, for the most part. _Black_ is strictly about formatting, nothing else. But because
_Black_ is still in [beta](../../index.rst), some edges are still a bit rough. To combat
issues, the equivalence of code after formatting is
[checked](../../the_black_code_style/current_style.md#ast-before-and-after-formatting)
with limited special cases where the code is allowed to differ. If issues are found, an
error is raised and the file is left untouched.
