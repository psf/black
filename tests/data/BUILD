# N.B.: This recursive glob is convenient but it also represents a large blob
# of files that will invalidate the tests that depend upon it whenever just 1
# file is changed. It may make sense to maintain finer-grained targets and
# dependencies on those targets by certain test files if test data invalidation
# ends up being the cause of a lot of needless test re-running.
files(sources=["**", "!BUILD"])
