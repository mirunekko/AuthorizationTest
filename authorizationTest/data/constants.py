import os

class Constants:
    try:
        login = os.getenv('LOGIN')
        password = os.getenv('PASSWORD')
    except KeyError:
        print("LOGIN OR PW WASN'T FOUND")