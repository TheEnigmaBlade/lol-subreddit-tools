#!/usr/bin/env python3

######################
# User configuration #
######################

subreddit = ""
user_exclude = []

slack_webhook = ""
slack_channels = []
slack_message = "_{title}_\n> {body}\n{permalink}"

user_agent = "script:Subreddit forwarder for Slack:v1.1 (by /u/TheEnigmaBlade), run for /r/{}".format(subreddit)
cache_file = "caches/{}.cache".format(subreddit)

##########################################
# DO NOT TOUCH ANYTHING AFTER THIS POINT #
##########################################

import os

if "SECRET_CONFIG" in os.environ:
	c = __import__(os.environ["SECRET_CONFIG"])
	globals().update({k: c.__dict__[k] for k in c.__dict__ if not k.startswith("_")})

# Slack

import requests

def send_message(msg):
	if slack_channels and len(slack_channels) > 0:
		for channel in slack_channels:
			print("Test to {}".format(channel))
			#resp = requests.post(slack_webhook, json={"text": msg, "channel": channel})
			#print(resp.status_code, resp.reason)
	else:
		resp = requests.post(slack_webhook, json={"text": msg})
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

def create_post_message(post):
	# TODO: support link posts
	if not post.is_self or not post.selftext:
		print("Post is not text")
		return None
	
	author = post.author.name.lower()
	if user_exclude and author in user_exclude:
		print("Excluded author")
		return None
		
	permalink = post.permalink
	title = post.title
	body = post.selftext[:140]
	body = body.replace("\n", " ").replace("  +", " ")
	author = post.author.name
	ttype = "text" if post.is_self else "link"
	
	return safe_format(slack_message, permalink=permalink, title=title, body=body, author=author, type=ttype)

import praw, cache

def main():
	print("Loading cache")
	seen_posts = cache.load_cached_storage(cache_file, default_size=30)
	
	print("Connecting to reddit")
	r = praw.Reddit(user_agent=user_agent)
	sub = r.get_subreddit(subreddit, fetch=False)
	
	print("Getting new")
	new = sub.get_new(limit=10)
	new = seen_posts.get_diff(new)
	print("New posts:")
	print(new)
	
	for post in new:
		msg = create_post_message(post)
		if msg:
			print()
			print(msg)
			send_message(msg)

if __name__ == "__main__":
	main()
