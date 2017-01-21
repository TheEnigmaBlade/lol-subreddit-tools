#!/usr/bin/env python3

######################
# User configuration #
######################

oauth_public = ""
oauth_secret = ""
username = ""
password = ""
user_agent = "script:Dev CSS uploader:v1.2 (by /u/TheEnigmaBlade), run by /u/{}".format(username)

from_subreddit	= ""
to_subreddit	= ""

##########################################
# DO NOT TOUCH ANYTHING AFTER THIS POINT #
##########################################

import os
import praw

_oauth_scopes={"modconfig"}

if "SECRET_CONFIG" in os.environ:
	c = __import__(os.environ["SECRET_CONFIG"])
	globals().update({k: c.__dict__[k] for k in c.__dict__ if not k.startswith("_")})

r = None

def init_reddit():
	global r
	r = praw.Reddit(client_id=oauth_public, client_secret=oauth_secret,
					username=username, password=password,
					user_agent=user_agent)

def transfer():
	try:
		print("Retrieving CSS from /r/{}".format(from_subreddit))
		css = r.subreddit(from_subreddit).stylesheet().stylesheet
		#if "errors" in response and len(response["errors"] > 0):
		#	errors = response["errors"]
		#	print("Failed!")
		#	print("Error when updating stylesheet", file=sys.stderr)
		#	print(errors, file=sys.stderr)
		#	return
			
		print("Setting CSS on /r/{}".format(to_subreddit))
		r.subreddit(to_subreddit).stylesheet.update(css)
		#if "errors" in response and len(response["errors"]) > 0:
		#	errors = response["errors"]
		#	print("Failed!")
		#	print("Error when updating stylesheet", file=sys.stderr)
		#	print(errors, file=sys.stderr)
		#	return
			
		print("Done!")
	except praw.exceptions.APIException as e:
		print("Bad CSS")
		print(e)
	#except praw.errors.OAuthInvalidToken:
	#	print("Invalid auth")

# Main

if __name__ == "__main__":
	init_reddit()
	transfer()
