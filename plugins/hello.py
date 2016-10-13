outputs = []


def process_message(data):
    if "hello" in data["text"]:
        outputs.append([
            data["channel"],
            "Hello! Your internal name is {}; I don't know about real names yet :cry:".format(data["user"])
        ])
