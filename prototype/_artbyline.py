# -*- coding: utf-8 -*-
"""The byline and the share row move under the picture.

The order was tag, headline, deck, byline, picture, story, share - so the
byline sat between the deck and the photograph, splitting the two halves of
the headline block, and sharing was a thousand words below the thing anybody
would want to share.

Now the top of the page is the story's own words - tag, headline, deck -
then the picture, and under it the line that says who wrote it and when,
with the share row beside it. Everything you would do with the story before
reading it, in one band, under the image and above the first paragraph.

Share also loses its label. A row of buttons that say X, Facebook, Email and
Copy link does not need the word Share in front of it, and the label was
only ever there because the row began the section rather than sitting in it.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ---------------------------------------- byline out from above the picture
sub("""        {post.blurb && <p className="artdeck">{post.blurb}</p>}
        <p className="bsm" style={{ color: "var(--muted)", fontWeight: 600 }}>
          {post.author ? post.author + " · " : ""}{fmtDate(post.date)}
        </p>

        {post.image && (
          <img className="artcover" src={post.image} alt="" />
        )}
""",
    """        {post.blurb && <p className="artdeck">{post.blurb}</p>}

        {post.image && (
          <img className="artcover" src={post.image} alt="" />
        )}

        {/* Who wrote it, when, and what you can do with it - one band under
            the picture and above the first paragraph, which is where a reader
            is deciding whether to go on. */}
        <div className="artbyline">
          <p className="artbylinewho">
            {post.author ? post.author + " · " : ""}{fmtDate(post.date)}
          </p>
          <ShareRow site={site} post={post} />
        </div>
""")

# --------------------------------------------- and share out from the foot
sub("""          {renderArticle(post.body || "", onPlayerName)}
        </div>

        <ShareRow site={site} post={post} />
""",
    """          {renderArticle(post.body || "", onPlayerName)}
        </div>
""")

# ------------------------------------------------------ the row loses its label
sub("""    <div className="artshare">
      <p className="artlabel">Share</p>
      <div className="artsharebtns">""",
    """    {/* No "Share" in front of it: a row reading X, Facebook, Email, Copy link
        says what it is. The label existed because this used to open a section
        of its own rather than sit inside a line. */}
    <div className="artshare">
      <div className="artsharebtns">""")

sub("""      </div>
    </div>
  );
}

/* ---------------- Public article page ---------------- */""",
    """      </div>
    </div>
  );
}

/* ---------------- Public article page ---------------- */""")

# ------------------------------------------------------------------- CSS
sub(""".artshare { display: flex; align-items: center; flex-wrap: wrap; gap: 10px 14px;""",
    """/* The byline and the share row on one line, wrapping to two when there is
   not room - the date reads first on both, which is the order it is wanted
   in. */
.artbyline { display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 12px 18px; margin: 16px 0 6px;
  padding-bottom: 16px; border-bottom: 1px solid var(--border); }
.artbylinewho { margin: 0; font-size: 13.5px; font-weight: 600; color: var(--muted); }
.artbyline .artshare { margin: 0; padding: 0; border: 0; }

.artshare { display: flex; align-items: center; flex-wrap: wrap; gap: 10px 14px;""")

io.open(p, 'w', encoding='utf-8').write(s)
print('byline and share sit under the picture')
