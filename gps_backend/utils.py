def dotenv_load():
    res: dict[str, str] = {}
    try:
        with open('.env') as f:
            for line in f:
                # Handle lines that do not have an equals sign
                try:
                    key, value = line.strip().split('=', 1)
                    res[key] = value
                except ValueError:
                    pass
    except FileNotFoundError:
        pass

    return res
