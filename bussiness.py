def format_input_text(in_str):
    return "".join(entry + "\n" for entry in list(filter(None, in_str.split("\n"))))