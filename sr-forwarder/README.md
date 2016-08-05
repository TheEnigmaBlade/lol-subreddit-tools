# Slack subreddit forwarder

Forwards posts from a subreddit to Slack using a web hook integration.

## Requirements

* Python 3.2+ (tested on 3.5)
* Slack server and configured web hook integration

Additional Python requirements are outlined in `requirements.txt`.

## Usage

    python sr_forwarder.py

Should be set up with a scheduler (ex. cron) to run regularly.

## Configuration

The following settings are available at the top of `sr_forwarder.py`.

|Name|Type|Description|Example|
:--|:-:|:--|:--
subreddit|string|Subreddit being forwarded (without `/r/`)|`leagueofmeta`
user_exclude|list(string)|List of post authors to ignore (without `/u/`), or `None`.|`["mod1", "mod2", "annoying_user"]`
|||
slack_webhook|string|Slack webhook URL|`https://hooks.slack.com/services/f7aosydf/k09823ya/fj0-92waosfv0q873-r182d7g`
slack_channels|list(string)|List of Slack channels to send post messages. If `None` or empty, sends to the integration's default channel.|`["#general", "#meta_sr"]`
slack_message|string|Message to send. Formatted with `{permalink}`, `{title}`, `{body}`, `{author}`, and `{type}`.
