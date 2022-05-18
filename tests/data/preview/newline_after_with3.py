with open("/path/to/file.txt", mode="r") as read_file:

    with open("/path/to/output_file.txt", mode="w") as write_file:

        write_file.writelines(read_file.readlines())

# output

with open("/path/to/file.txt", mode="r") as read_file:
    with open("/path/to/output_file.txt", mode="w") as write_file:
        write_file.writelines(read_file.readlines())
