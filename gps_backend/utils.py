def dotenv_load():
    with open('.env') as f:
        res: dict[str, str] = {}
        for line in f:
            key, value = line.strip().split('=', 1)
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            res[key] = value
        return res
