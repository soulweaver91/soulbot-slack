from services import users as usersvc

outputs = []


def process_message(data):
    if "hello" in data["text"]:
        outputs.append([
            data["channel"],
            "Hello, {}!".format(usersvc.get_user_name(data["user"]))
        ])
