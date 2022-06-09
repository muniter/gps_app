from . import database
from . import models

def main():
    print('Starting')
    models.Base.metadata.create_all(bind=database.engine)
    from . import bootstrap
    bootstrap.run()

if __name__ == "__main__":
    main()


