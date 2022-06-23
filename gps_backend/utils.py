def dotenv_load():
    res: dict[str, str] = {}
    try:
        with open('.env') as f:
            for line in f:
                key, value = line.strip().split('=', 1)
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                res[key] = value
    except FileNotFoundError:
        pass

    return res
