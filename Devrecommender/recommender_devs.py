import dev_recommender
import sys

if __name__ == "__main__":
    arguments = sys.argv[1:]
    owner = arguments[0]
    repository = arguments[1]
    k = int(arguments[2])
    decimal_places = int(arguments[3])
    recommender = dev_recommender.Dev_recomender(owner, repository, '')

    recommender.recomender_substitutes(k, decimal_places)
