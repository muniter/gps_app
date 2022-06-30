from . import *
import os

if __name__ == '__main__':
    app.run(debug=os.environ.get('ENV') != 'production')
