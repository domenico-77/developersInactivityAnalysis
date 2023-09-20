import dev_recommender
import sys

if __name__ == "__main__":
    arguments = sys.argv[1:]
    owner = arguments[0]
    repository = arguments[1]
    token = arguments[2]
    recommender = dev_recommender.Dev_recomender(owner, repository, token)