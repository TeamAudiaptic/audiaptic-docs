#!/usr/bin/env python3
"""Turn every Audiaptic repo's CHANGELOG.yml into one Docusaurus blog post per day.

All four repos are public, so this reads them over plain HTTPS with no
credentials. It only ever writes inside the repo it runs in, and only ever
touches files matching BLOG_DIR/<date>-<SLUG_SUFFIX>.mdx - your hand-written
blog posts are never read, rewritten or deleted.

Days are grouped in the team's local timezone (LOCAL_TZ), not UTC, so an
evening merge lands on the day it felt like rather than the next one.

Each generated post looks like:

    ---
    slug: changelog-2026-09-15
    title: 'Changelog: September 15, 2026'
    authors: [Liam, Josh]
    tags: [changelog, changes-server]
    date: 2026-09-15
    ---

    **3 changes** across **2 repos** from **2 contributors**.

    {/* truncate */}

    ## Server
    ### Liam (@shackhorn)
    <emoji> **Feature** Per-layer solo and mute [#12](link)

"""

import os
import re
import sys
import urllib.error
import urllib.request
from collections import defaultdict, OrderedDict
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import yaml

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ORG = "TeamAudiaptic"              # GitHub org or user that owns the repos
BRANCH = "changelog"               # branch holding CHANGELOG.yml in each repo

BLOG_DIR = "blog"                  # Docusaurus blog directory
SLUG_SUFFIX = "changelog"          # files are <date>-<SLUG_SUFFIX>.mdx

# Timezone used to decide which day a change belongs to. Stored timestamps stay
# in UTC; this only affects grouping and display, and handles DST on its own.
LOCAL_TZ = ZoneInfo("America/New_York")

# Author key from blog/authors.yml used when a day has no mapped contributors.
POST_AUTHOR = "TeamAudiaptic"

# GitHub login -> key in blog/authors.yml. Contributors listed here are credited
# as authors on the days they shipped something, and their name is shown in the
# section heading. Logins not in this map fall back to the raw login, so an
# incomplete map can never break the build.
AUTHOR_MAP = {
    "shackhorn": "Liam",
    "dcr8024": "Darren",
    "cpw9783": "Chris",
    "ejs8021": "Elijah",
    "fangkristen": "Kristen",
    "TashiTseten": "Tashi",
    "Josh-mitch": "Josh",
}

# Tags applied to every generated post. Add these to blog/tags.yml to avoid
# Docusaurus' "inline tag" warning.
TAGS = ["changelog"]

# Heading level for repo sections. Author headings are one deeper. The post
# title is the page <h1>, so repos start at <h2>.
HEADING_BASE = 2

# Repo -> label. Order here is the order sections appear within a post.
REPOS = OrderedDict([
    ("audiaptic-server", "Server"),
    ("audiaptic-client", "Client"),
    ("audiaptic-max", "Max/MSP"),
    ("audiaptic-docs", "Docs"),
])

# Repo label -> extra tags applied to any post containing changes from that
# repo. These also need to exist in blog/tags.yml.
REPO_TAGS = {
    "Server": ["changes-server"],
    "Client": ["changes-client"],
    "Max/MSP": ["changes-max"],
    "Docs": ["changes-docs"],
}

# Fallback display for entries written before emoji/label were stored.
TYPE_LABEL = {
    "breaking": ("\U0001F4A5", "Breaking change"),
    "feature": ("✨", "Feature"),
    "fix": ("\U0001F41B", "Fix"),
    "perf": ("⚡", "Performance"),
    "refactor": ("♻️", "Refactor"),
    "docs": ("\U0001F4DD", "Documentation"),
    "maintenance": ("\U0001F527", "Maintenance"),
}

# Order changes appear under a single author. Breaking changes lead.
TYPE_ORDER = ["breaking", "feature", "fix", "perf", "refactor", "docs", "maintenance"]

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

RAW_URL = "https://raw.githubusercontent.com/{org}/{repo}/{branch}/CHANGELOG.yml"

CODE_SPAN = re.compile(r"(`+)(?:.|\n)*?\1")


# ---------------------------------------------------------------------------


def local_day(timestamp):
    """A stored UTC timestamp -> YYYY-MM-DD in LOCAL_TZ, or "" if unparseable."""
    try:
        parsed = datetime.fromisoformat(timestamp)
    except (TypeError, ValueError):
        return ""

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(LOCAL_TZ).strftime("%Y-%m-%d")


def escape_mdx(text):
    """Make text safe for MDX.

    MDX treats `{` as the start of an expression and `<` as the start of a tag,
    so a PR description containing either would break the site build. Inline
    code is already literal in MDX, so those spans are left alone.
    """
    if not text:
        return ""

    out = []
    position = 0

    for match in CODE_SPAN.finditer(text):
        chunk = text[position:match.start()]
        out.append(chunk.replace("{", "&#123;").replace("<", "&lt;"))
        out.append(match.group(0))
        position = match.end()

    out.append(text[position:].replace("{", "&#123;").replace("<", "&lt;"))
    return "".join(out)


def pretty_date(day):
    """2026-09-15 -> September 15, 2026."""
    try:
        parsed = date.fromisoformat(day)
    except ValueError:
        return day
    return "%s %d, %d" % (MONTHS[parsed.month - 1], parsed.day, parsed.year)


def fetch(repo):
    """Return the parsed entries for one repo, or None if it has no changelog."""
    url = RAW_URL.format(org=ORG, repo=repo, branch=BRANCH)

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        if error.code == 404:
            print("  %s: no CHANGELOG.yml yet, skipping" % repo)
            return None
        print("  %s: HTTP %d" % (repo, error.code), file=sys.stderr)
        raise
    except urllib.error.URLError as error:
        print("  %s: %s" % (repo, error.reason), file=sys.stderr)
        raise

    data = yaml.safe_load(raw) or {}
    entries = data.get("entries")

    if not isinstance(entries, list):
        print("  %s: no entries list, skipping" % repo)
        return None

    print("  %s: %d entries" % (repo, len(entries)))
    return entries


def collect():
    """Return {day: {repo_label: {author: [record, ...]}}}, keyed by local day."""
    tree = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for repo, label in REPOS.items():
        entries = fetch(repo)
        if not entries:
            continue

        for entry in entries:
            time = str(entry.get("time", ""))
            day = local_day(time)

            if not day:
                print("  ! entry %s in %s has no usable date, skipping"
                      % (entry.get("id"), repo), file=sys.stderr)
                continue

            author = entry.get("author", "unknown")

            for change in entry.get("changes", []):
                change_type = str(change.get("type", "fix")).lower()
                fallback = TYPE_LABEL.get(change_type, ("", change_type.title()))

                tree[day][label][author].append({
                    "type": change_type,
                    "emoji": change.get("emoji") or fallback[0],
                    "label": change.get("label") or fallback[1],
                    "message": change.get("message", ""),
                    "pr": entry.get("pr"),
                    "url": entry.get("url", ""),
                    "time": time,
                })

    return tree


def type_rank(record):
    if record["type"] in TYPE_ORDER:
        return TYPE_ORDER.index(record["type"])
    return len(TYPE_ORDER)


def post_authors(day_tree):
    """Author keys for a day's frontmatter, from AUTHOR_MAP where possible."""
    logins = {author for repo in day_tree.values() for author in repo}
    mapped = sorted({AUTHOR_MAP[login] for login in logins if login in AUTHOR_MAP})
    return mapped or [POST_AUTHOR]


def post_tags(day_tree):
    """Tags for a day's frontmatter: the defaults plus one set per repo touched."""
    tags = set(TAGS)

    for label in day_tree:
        tags.update(REPO_TAGS.get(label, []))

    return sorted(tags)


def render_post(day, day_tree):
    repo_h = "#" * HEADING_BASE
    author_h = "#" * (HEADING_BASE + 1)

    change_count = sum(
        len(records)
        for repo in day_tree.values()
        for records in repo.values()
    )
    repo_count = len(day_tree)
    people = {author for repo in day_tree.values() for author in repo}

    def plural(count, word):
        return "%d %s%s" % (count, word, "" if count == 1 else "s")

    lines = [
        "---",
        "slug: %s-%s" % (SLUG_SUFFIX, day),
        "title: 'Changelog: %s'" % pretty_date(day),
        "authors: [%s]" % ", ".join(post_authors(day_tree)),
        "tags: [%s]" % ", ".join(post_tags(day_tree)),
        "date: %s" % day,
        "---",
        "",
        "**%s** across **%s** from **%s**." % (
            plural(change_count, "change"),
            plural(repo_count, "repo"),
            plural(len(people), "contributor"),
        ),
        "",
        "{/* truncate */}",
        "",
    ]

    for label in REPOS.values():
        if label not in day_tree:
            continue

        lines += ["%s %s" % (repo_h, label), ""]

        for author in sorted(day_tree[label], key=str.lower):
            # "Liam (@shackhorn)", or just "@login" when the login is unmapped.
            name = AUTHOR_MAP.get(author)
            heading = "%s (@%s)" % (name, author) if name else "@%s" % author
            lines += ["%s %s" % (author_h, heading), ""]

            for record in sorted(day_tree[label][author],
                                 key=lambda r: (type_rank(r), r["time"])):
                if record["pr"] and record["url"]:
                    reference = " [#%s](%s)" % (record["pr"], record["url"])
                else:
                    reference = ""

                lines += [
                    "%s **%s** %s%s" % (
                        record["emoji"],
                        escape_mdx(record["label"]),
                        escape_mdx(record["message"]),
                        reference,
                    ),
                    "",
                ]

    return "\n".join(lines).rstrip("\n") + "\n"


def prune(tree):
    """Delete generated posts for days that no longer have any entries.

    Only files named <date>-<SLUG_SUFFIX>.mdx are considered, so hand-written
    posts and dated post folders are never touched. This is what keeps a
    corrected timestamp from stranding a stale file behind.
    """
    if not os.path.isdir(BLOG_DIR):
        return 0

    expected = {"%s-%s.mdx" % (day, SLUG_SUFFIX) for day in tree}
    suffix = "-%s.mdx" % SLUG_SUFFIX
    removed = 0

    for name in sorted(os.listdir(BLOG_DIR)):
        path = os.path.join(BLOG_DIR, name)

        if not os.path.isfile(path) or not name.endswith(suffix):
            continue

        if name not in expected:
            os.remove(path)
            print("  removed stale %s" % path)
            removed += 1

    return removed


def main():
    if ORG == "CHANGE-ME":
        print("Set ORG at the top of this script first.", file=sys.stderr)
        return 1

    print("Fetching changelogs:")
    tree = collect()

    if not tree:
        print("Nothing to publish yet.")
        return 0

    os.makedirs(BLOG_DIR, exist_ok=True)

    written = 0
    for day, day_tree in sorted(tree.items()):
        path = os.path.join(BLOG_DIR, "%s-%s.mdx" % (day, SLUG_SUFFIX))
        content = render_post(day, day_tree)

        # Skip the write when nothing changed, so git stays quiet.
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                if handle.read() == content:
                    continue

        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)

        print("  wrote %s" % path)
        written += 1

    removed = prune(tree)

    print("%d day(s) in the changelog, %d post(s) written or updated, "
          "%d removed." % (len(tree), written, removed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
