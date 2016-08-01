#!/usr/bin/env python3

######################
# User configuration #
######################

subreddit = ""
queues = ["modqueue"]
thresholds = [
	(20, "There are {count} in {queue}. {url}")
]

slack_webhook = ""
slack_channels = ["general"]

oauth_public = ""
oauth_secret = ""
username = ""
password = ""
user_agent = "script:Queue size monitor for Slack:v1.1 (by /u/TheEnigmaBlade), run for /r/{}".format(subreddit)

cache_file = "caches/count_{subreddit}_{queue}.txt"

##########################################
# DO NOT TOUCH ANYTHING AFTER THIS POINT #
##########################################

_oauth_scopes = {"read"}

import os

if "SECRET_CONFIG" in os.environ:
	c = __import__(os.environ["SECRET_CONFIG"])
	globals().update({k: c.__dict__[k] for k in c.__dict__ if not k.startswith("_")})

# Slack

import requests

def send_message(msg):
	for channel in slack_channels:
		print("Sending to #{}".format(channel))
		print(msg)
		resp = requests.post(slack_webhook, json={"text": msg, "channel": channel})
		print(resp.status_code, resp.reason)

# Caching

def get_last_count(queue):
	try:
		with open(cache_file.format(subreddit=subreddit, queue=queue), "r") as f:
			return int(f.readline().strip())
	except FileNotFoundError as e:
		print("Failed to get last count", file=sys.stderr)
		print(e)
		return 0

def save_count(queue, count):
	try:
		os.makedirs(os.path.dirname(cache_file), exist_ok=True)
		with open(cache_file.format(subreddit=subreddit, queue=queue), "w") as f:
			f.write("{}".format(count))
	except FileNotFoundError as e:
		print("Failed to save time", file=sys.stderr)
		print(e)

# Helpers

class _SafeDict(dict):
	def __missing__(self, key):
		return "{" + key + "}"

def safe_format(s, **kwargs):
	"""
	A safer version of the default str.format(...) function.
	Ignores unused keyword arguments and unused '{...}' placeholders instead of throwing a KeyError.
	:param s: The string being formatted
	:param kwargs: The format replacements
	:return: A formatted string
	"""
	return s.format_map(_SafeDict(**kwargs))

# Main

import sys, praw_script_oauth
from operator import itemgetter

def threshold_index(count):
	for i, t in enumerate(thresholds):
		if count >= t[0]:
			return i, t[1]
	return -1, None

def format_message(msg, queue, num_things):
	url = "https://reddit.com/r/{}/about/{}".format(subreddit, queue)
	return safe_format(msg, queue=queue, count=num_things, url=url)

def main():
	global thresholds
	thresholds.sort(key=itemgetter(0), reverse=True)
	
	print("Connecting to reddit")
	r = praw_script_oauth.connect(oauth_public, oauth_secret, username, password, oauth_scopes=_oauth_scopes,
								  useragent=user_agent, script_key="queue_size_{}".format(subreddit))
	r.config.cache_timeout = 0
	
	for queue in queues:
		print("Getting {}".format(queue))
		
		# Get queue things
		if queue == "modqueue":
			things = r.get_mod_queue(subreddit, limit=100)
		elif queue == "unmoderated":
			things = r.get_unmoderated(subreddit, limit=100)
		elif queue == "spam":
			things = r.get_spam(subreddit, limit=100)
		else:
			print("\"{}\" is not a valid queue. Use \"modqueue\", \"unmoderated\", or \"spam\".".format(queue), file=sys.stderr)
			return
		
		# Do stuff
		things = list(things)
		num_things = len(things)
		print("Num things: {}".format(num_things))
		
		# Check cache
		prev_count = get_last_count(queue)
		prev_i, _ = threshold_index(prev_count)
		
		# Check thresholds
		i, msg = threshold_index(num_things)
		if i > prev_i:
			print("It's over the threshold!!!")
			msg = format_message(msg, queue, num_things)
			send_message(msg)
		
		save_count(queue, num_things)

if __name__ == "__main__":
	main()
