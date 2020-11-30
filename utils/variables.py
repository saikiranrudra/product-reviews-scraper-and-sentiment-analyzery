"""
A Singleton class used to store Constant Variables
1. URL

"""


class Variables:
    __instance = None

    # Class Variables
    URL = {
        'AMAZON': 'https://www.amazon.in/s?k=',
        'FLIP_KART_SEARCH': 'https://www.flipkart.com/search?q=',
        'FLIP_KART': 'https://www.flipkart.com'
    }

    @staticmethod
    def get_instance():
        if Variables.__instance is None:
            Variables()

        return Variables.__instance

    def __init__(self):
        if Variables.__instance is not None:
            raise Exception("This is a Singleton Class")
        else:
            Variables.__instance = self
