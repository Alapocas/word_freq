import pickle, os

PATH = os.path.dirname(__file__)+"/total.pickle"
diction = pickle.load(open(PATH, "rb"))
