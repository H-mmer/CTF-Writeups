dicti = {}


def add_achievement(clientid, name, description):
    global dicti
    dicti.setdefault(clientid, {})
    dicti[clientid][name] = description
