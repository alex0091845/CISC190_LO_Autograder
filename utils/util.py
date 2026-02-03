def clean_assignment_name(name: str) -> str:
    # remove any prefix from the assignment name
    try:
        if name.index(')') > -1:
            name = name[name.index(')') + 1 :]
    except ValueError:
        pass
    return name.strip()