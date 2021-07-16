from urllib.parse import urlparse
import codecs
import json
import datetime
import os

__tinypub_version__ = "0.0.3"

from nikola.plugin_categories import Task
from nikola.utils import (
    config_changed, copy_file, LocaleBorg, makedirs, unicode_str,
)

class TinyPub(Task):
    """Create some ActivityPub objects for posts."""

    name = "tinypub"

    def gen_tasks(self):
        self.site.scan_posts()

        kw = {
            "tinypub_version": __tinypub_version__,
            "translations": self.site.config['TRANSLATIONS'],
            "output_folder": self.site.config["OUTPUT_FOLDER"],
            "base_url": self.site.config["BASE_URL"],
            "blog_author": self.site.config["BLOG_AUTHOR"],
            "blog_title": self.site.config["BLOG_TITLE"],
            "blog_description": self.site.config["BLOG_DESCRIPTION"],
            "pub_author": self.site.config["PUB_AUTHOR"],
            "pub_name": self.site.config["PUB_NAME"],
            "pub_icon": self.site.config["PUB_ICON"],
            "pub_keypem": self.site.config["PUB_KEYPEM"],
            "pub_notice": self.site.config["PUB_NOTICE"],
            "timeline": self.site.timeline,
        }
        posts = self.site.timeline[:]

        def get_actor_url():
            return kw["base_url"] + "tinypub/" + kw["pub_name"]

        def write_webfinger():
            actor_url = get_actor_url()
            webfinger = {
                "aliases": [
                    actor_url + ".jsonld"
                ],
                "links": [
                    {
                        "href": actor_url + ".jsonld",
                        "rel": "self",
                        "type": "application/activity+json"
                    }
                ],
                "subject": (
                    "acct:"
                    + kw["pub_name"]
                    + "@"
                    + (urlparse(kw["base_url"]).netloc)
                )
            }
            path = os.path.join(kw["output_folder"],
                                ".well-known", "webfinger")
            makedirs(os.path.dirname(path))
            with codecs.open(path, 'wb+', 'utf8') as fd:
                fd.write(json.dumps(webfinger))

        def write_actor():
            actor_url = get_actor_url()
            actor = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "following": actor_url + ".following.jsonld",
                "followers": actor_url + ".followers.jsonld",
                "icon": {
                    "mediaType": "image/png",
                    "type": "Image",
                    "url": kw["base_url"] + kw["pub_icon"],
                },
                "id": actor_url + ".jsonld",
                "inbox": actor_url + ".inbox.jsonld",
                "movedTo": kw["pub_author"],
                "name": kw["blog_title"](),
                "outbox": actor_url + ".outbox.jsonld",
                "preferredUsername": kw["pub_name"],
                "publicKey": {
                    "id": actor_url + ".jsonld#key",
                    "owner": actor_url + ".jsonld",
                    "publicKeyPem": kw["pub_keypem"],
                },
                "summary": (
                    kw["pub_notice"] + "<br><br>"
                    + kw["blog_description"]()
                ),
                "type": "Person",
                "url": kw["base_url"],
            }
            path = os.path.join(kw["output_folder"],
                                "tinypub", kw["pub_name"])
            makedirs(os.path.dirname(path))
            with codecs.open(path + ".jsonld", 'wb+', 'utf8') as fd:
                fd.write(json.dumps(actor))
            with codecs.open(path + ".following.jsonld", 'wb+', 'utf8') as fd:
                fd.write(json.dumps({
                    "@context": "https://www.w3.org/ns/activitystreams",
                    "attributedTo": actor["id"],
                    "id": actor["following"],
                    "orderedItems": [],
                    "totalItems": 0,
                    "type": "OrderedCollection"
                }))
            with codecs.open(path + ".followers.jsonld", 'wb+', 'utf8') as fd:
                fd.write(json.dumps({
                    "@context": "https://www.w3.org/ns/activitystreams",
                    "attributedTo": actor["id"],
                    "id": actor["followers"],
                    "orderedItems": [],
                    "totalItems": 0,
                    "type": "OrderedCollection"
                }))
            with codecs.open(path + ".inbox.jsonld", 'wb+', 'utf8') as fd:
                fd.write(json.dumps({
                    "@context": "https://www.w3.org/ns/activitystreams",
                    "attributedTo": actor["id"],
                    "id": actor["inbox"],
                    "orderedItems": [],
                    "totalItems": 0,
                    "type": "OrderedCollection"
                }))
            with codecs.open(path + ".outbox.jsonld", 'wb+', 'utf8') as fd:
                fd.write(json.dumps({
                    "@context": "https://www.w3.org/ns/activitystreams",
                    "attributedTo": actor["id"],
                    "id": actor["outbox"],
                    "orderedItems": [],
                    "totalItems": 0,
                    "type":"OrderedCollection"
                }))

        def write_file(path, post, lang):
            published = post.date
            if isinstance(post.date, datetime.date):
                published = datetime.datetime.combine(post.date, datetime.datetime.min.time())
            isoPublished = (
                published.astimezone(datetime.timezone.utc)
                .replace(microsecond=0).isoformat()
                .replace("+00:00", "Z")
            )
            pubPost = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "attributedTo": get_actor_url() + ".jsonld",
                "content": post.text(lang),
                "id": post.permalink(lang, True, ".jsonld"),
                "published": isoPublished,
                "summary": post.title(lang),
                "to": [ "https://www.w3.org/ns/activitystreams#Public" ],
                "cc": [ "https://www.w3.org/ns/activitystreams#Public" ],
                "type": "Note",
                "url": post.permalink(lang, True),
            }
            makedirs(os.path.dirname(path))
            with codecs.open(path, 'wb+', 'utf8') as fd:
                fd.write(json.dumps(pubPost))

        webfinger_path = os.path.join(kw["output_folder"],
                                      ".well-known", "webfinger")
        yield {
            'basename': 'tinypub',
            'name': 'webfinger',
            'file_dep': [],
            'targets': [
                webfinger_path
            ],
            'actions': [(write_webfinger, ())],
            'task_dep': ['render_posts'],
            'uptodate': [config_changed(kw)],
        }
        actor_path = os.path.join(kw["output_folder"],
                                  "tinypub", kw["pub_name"])
        yield {
            'basename': 'tinypub',
            'name': 'actor.jsonld',
            'file_dep': [],
            'targets': [
                actor_path + ".jsonld",
                actor_path + ".inbox.jsonld",
                actor_path + ".outbox.jsonld",
                actor_path + ".following.jsonld",
                actor_path + ".followers.jsonld",
            ],
            'actions': [(write_actor, ())],
            'task_dep': ['render_posts'],
            'uptodate': [config_changed(kw)],
        }
        for lang in kw["translations"]:
            for i, post in enumerate(posts):
                out_path = post.destination_path(lang, ".jsonld")
                out_file = os.path.join(kw['output_folder'], out_path)
                task = {
                    'basename': 'tinypub',
                    'name': out_file,
                    'file_dep': post.fragment_deps(lang),
                    'targets': [out_file],
                    'actions': [(write_file, (out_file, post, lang))],
                    'task_dep': ['render_posts'],
                    'uptodate': [config_changed({
                        1: post.text(lang),
                        2: post.title(lang),
                        3: post.permalink(lang),
                        4: post.title(lang),
                        5: __tinypub_version__,
                    })]
                }
                yield task
