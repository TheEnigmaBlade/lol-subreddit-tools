# Queue size monitor

Monitors mod queue sizes (modqueue, unmoderated, and spam), and sends a message to Slack if they go over a threshold.

*Note:* Still being developed.

## Requirements

* Python 3+ (tested on 3.5)

Additional Python requirements are outlined in `requirements.txt`.

## Usage

    python queue_size.py

Should be set up with a scheduler (ex. cron) to run regularly.

## Configuration

The following settings are available at the top of `queue_size.py`.

|Name|Type|Description|Example|
:--|:-:|:--|:--
subreddit|string|Subreddit being monitored (without `/r/`)|`"mysubreddit"`
queues|list(string)|List of queues being monitored. Available queues: `modqueue`, `unmoderated`, `spam`|`["modqueue"]`
thresholds|list(tuple)|List of threshold tuples comprised of an int and string.|`[(20, "This message is sent for queues over 20!")]`
|||
slack_webhook|string|Slack web hook integration URL|`"https://hooks.slack.com/services/we3srhas/34rygway/f02q9uaw98usdijfhaosidjad"`
slack_channels|list(string)|List of Slack channels to send messages. If `None` sends to the default integration channel.|`["general", "warnings"]`
slack_message|string|Message to send. Formatted with `{queue}`, `{count}`, and `{url}`.|`"{queue} has become super active: {posts} posts made in {time} seconds"`
