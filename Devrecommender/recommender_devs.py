import dev_recommender
import sys

if __name__ == "__main__":
    arguments = sys.argv[1:]
    owner = arguments[0]
    repository = arguments[1]
    token = arguments[2]
    k = arguments[3]
    decimal_places = arguments[4]
    recommender = dev_recommender.Dev_recomender(owner, repository, token)

    recommender.recomender_substitutes(k, decimal_places)