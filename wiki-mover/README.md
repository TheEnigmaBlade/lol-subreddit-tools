# Subreddit wiki mover

A simple script to bulk move Reddit wiki pages from one location to another.

For example, consider this wiki structure:

```
/r/mysubreddit/wiki
  | rules
  | config
      | sidebar
      | ...
  | weekly_updates
      | week_1
      | week_2
      | ...
  | archives
      | 2015
          | week_1
          | week_2
          | ...
```

If you want to archive the sub-pages of `weeky_updates` at the end of 2016, you can set `from_path` to `weekly_updates` and `to_path` to `archives/2016`.

## Requirements

* Python 3+ (tested on 3.5)

Additional Python requirements are outlined in `requirements.txt`.

## Usage

    python wiki_mover.py

## Configuration

The following settings are available at the top of `wiki_mover.py`.

|Name|Type|Description|Example|
:--|:-:|:--|:--
from_subreddit|string|The subreddit containing the wiki pages being moved (without `/r/`)|`mysubreddit`
from_path|string|The path to the wiki "folder" containing pages being moved (without `/wiki/`)|`weekly_updates`
to_subreddit|string|The subreddit to which wiki pages are being moved (without `/r/`)|`mysubreddit`
to_path|string|The path to the new wiki "folder"|`archives/2016`
keep_perms|bool|If `True`, each page retains its access permissions. If `False`, pages get default permissions.|
hide_old|bool|If `True`, hides old wiki pages.|
save_info|bool|If `True`, prepends moved pages with the original URL and latest revision time.|
wiki_reason|string|The wiki edit reason for new pages|`Archiving weekly updates from 2016`
