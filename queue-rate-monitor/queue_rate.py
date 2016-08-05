#!/usr/bin/env python3

######################
# User configuration #
######################

subreddit = ""
queue = "new"
rate_threshold = 1 / 2	# post / sec

slack_webhook = ""
slack_channels = ["general"]
slack_message = "{queue} has become super active: {posts} posts made in {time} seconds"

user_agent = "script:Queue monitor for Slack:v2.0 (by /u/TheEnigmaBlade), run for /r/{}".format(subreddit)
cache_file = "caches/last_time_{}_{}.txt".format(subreddit, queue)

##########################################
# DO NOT TOUCH ANYTHING AFTER THIS POINT #
##########################################

import os, sys

if "SECRET_CONFIG" in os.environ:
	c = __import__(os.environ["SECRET_CONFIG"])
	globals().update({k: c.__dict__[k] for k in c.__dict__ if not k.startswith("_")})

# Caching

from time import time

def get_time():
	try:
		with open(cache_file, "r") as f:
			return float(f.readline().strip())
	except FileNotFoundError as e:
		print("Failed to get time", file=sys.stderr)
		print(e)
		return time()
	
def save_time(t):
	try:
		os.makedirs(os.path.dirname(cache_file), exist_ok=True)
		with open(cache_file, "w") as f:
			f.write("{:.3f}".format(t))
	except FileNotFoundError as e:
		print("Failed to save time", file=sys.stderr)
		print(e)

# Slack

import requests

def send_message(msg):
	for channel in slack_channels:
		print("Sending to #{}".format(channel))
		resp = requests.post(slack_webhook, json={"text": msg, "channel": channel})
		print(resp.status_code, resp.reason)

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

import praw

def main():
	print("Connecting to reddit")
	r = praw.Reddit(user_agent=user_agent)
	r.config.cache_timeout = 0
	sub = r.get_subreddit(subreddit, fetch=False)
	
	last_time = get_time()
	
	print("Getting {}".format(queue))
	if queue == "new":
		new = sub.get_new(limit=10)
	elif queue == "rising":
		new = sub.get_rising(limit=10)
	else:
		print("\"{}\" is not a valid queue. Use \"new\" or \"rising\".".format(queue), file=sys.stderr)
		return
	new = [t for t in map(lambda p: p.created_utc, new) if t > last_time]
	
	num_new = len(new)
	print("Num new posts: {}".format(num_new))
	now = time()
	time_diff = now - last_time
	print("Time diff: {:.2f} sec".format(time_diff))
	rate = num_new/time_diff
	print("New rate: {:.2f} posts/sec".format(rate))
	
	save_time(now)
	
	if rate > rate_threshold:
		print("It's over the threshold!!!")
		msg = safe_format(slack_message, queue=queue, posts=num_new, time=int(time_diff), rate=rate)
		send_message(msg)

if __name__ == "__main__":
	main()
