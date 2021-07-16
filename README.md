# TinyPub

A plugin for [Nikola](https://getnikola.com/) to generate ActivityPub objects for your posts.

A post with a url like this `https://myblog.com/posts/my-first-post/` will end up with its corresponding ActivityPub object at `https://myblog.com/posts/my-first-post/index.jsonld`. And you might want to put that somewhere on your post by modifying your theme.

Also, one must guarantee that these files are served with correct headers (i.e. `Content-Type: application/activity+json`, etc.). Or else, most likely other servers will not recognize the obects.

## Usage

Put the files accordingly in your Nikola blog:

```
./plugins/tinypub/task_tinypub.py
./plugins/tinypub/tinypub.plugin
```

Append the contents in `conf.tinypub.py` to your `conf.py`, and then edit them to suit your needs.

If you are using [Vercel](https://vercel.com/) to host your blog, you might just use the `vercel.json` provided. Put it in the root folder in your blog:

```
./vercel.json
```

If you are not using Vercel, you will need to find a way to modify your headers.
