# flags: --preview
data = (
    item_preprocessor.handle_missing_values(strategy="mean")
    .multilabel_binarize(["tags"])
    .normalize(["price"], methods=["z-score"])
)
result = pipeline.preprocessor.handle_missing_values(strategy="mean").multilabel_binarize(["tags"])
short_chain = pipeline.prepare().run()
single_call = package.pipeline.handle_missing_values(strategy="mean", fallback="median", columns=["price"])

# output
data = (
    item_preprocessor
    .handle_missing_values(strategy="mean")
    .multilabel_binarize(["tags"])
    .normalize(["price"], methods=["z-score"])
)
result = (
    pipeline.preprocessor
    .handle_missing_values(strategy="mean")
    .multilabel_binarize(["tags"])
)
short_chain = pipeline.prepare().run()
single_call = package.pipeline.handle_missing_values(
    strategy="mean", fallback="median", columns=["price"]
)
