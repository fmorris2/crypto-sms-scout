import os
import backend.Scout

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

scout = backend.Scout.Scout()

scout.run()