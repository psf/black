while True:
    if something.changed:
        do.stuff()  # trailing comment
        # Comment belongs to the `if` block.
    # This one belongs to the `while` block.

    # Should this one, too?  I guess so.

# This one is properly standalone now.

for i in range(100):
    # first we do this
    if i % 33 == 0:
        break

    # then we do this
    print(i)
    # and finally we loop around

with open(some_temp_file) as f:
    data = f.read()

try:
    with open(some_other_file) as w:
        w.write(data)

except OSError:
    print("problems")

if __name__ == "__main__":
    main()
