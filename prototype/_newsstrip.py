# -*- coding: utf-8 -*-
"""The news index loses its boxes and everything but the picture, the headline
and the date.

A card with a border, a white ground, a tag, a headline, a blurb, an author
and a date is seven things asking to be read before you know whether you
want to read the story. The picture and the headline do that work; the rest
is furniture around them.

So the boxes go. The image keeps its corners and the words sit under it on
the page, which is what an index of pictures wants to be - and with the tag,
blurb and byline gone there is nothing left for a border to hold together.

And the tiers stand further apart. Two across, then four, then six is a
change of rank rather than a continuation, and at fourteen pixels the three
read as one grid that keeps changing its mind.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------ the card loses its load
sub("""                    <div className="newscardart">
                      <img src={n.image || STOCK_IMAGES[i % STOCK_IMAGES.length]} alt="" loading="lazy"
                        onError={(e) => { e.currentTarget.style.visibility = "hidden"; }} />
                      <span className="newstag">{n.tag}</span>
                    </div>
                    <div className="newscardbody">
                      <h2 className="newscardtitle">{n.title}</h2>
                      {/* The archive gets a headline and a date. A blurb on a
                          card this size is three lines of grey. */}
                      {n.blurb && tier !== "rest" && <p className="newscardblurb">{n.blurb}</p>}
                      <p className="newscardmeta">
                        {n.author ? n.author + " · " : ""}{fmtDate(n.date)}
                      </p>
                    </div>""",
    """                    {/* The picture and the headline are what decide whether
                        anybody opens it. A tag, a blurb and a byline are three
                        more things to read first. */}
                    <div className="newscardart">
                      <img src={n.image || STOCK_IMAGES[i % STOCK_IMAGES.length]} alt="" loading="lazy"
                        onError={(e) => { e.currentTarget.style.visibility = "hidden"; }} />
                    </div>
                    <div className="newscardbody">
                      <h2 className="newscardtitle">{n.title}</h2>
                      <p className="newscardmeta">{fmtDate(n.date)}</p>
                    </div>""")

# ------------------------------------------------------------------- CSS
sub(""".newscard { display: flex; flex-direction: column; background: #fff;
  border: 1px solid var(--border); border-radius: 12px; overflow: hidden;
  cursor: pointer; }
.newscard:hover { border-color: var(--blue); }
.newscardart { position: relative; aspect-ratio: 16 / 9; background: var(--ice); }
.newscardart img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.newscardbody { padding: 16px 18px 18px; display: flex; flex-direction: column; gap: 7px; }""",
    """/* No box. With the tag, the blurb and the byline gone there is nothing left
   for a border to hold together, and a rule around a picture and two lines
   is furniture. The picture keeps its corners; the words sit on the page. */
.newscard { display: flex; flex-direction: column; cursor: pointer; }
.newscardart { position: relative; aspect-ratio: 16 / 9; background: var(--ice);
  border-radius: 10px; overflow: hidden; }
.newscardart img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;
  transition: transform 0.35s ease; }
.newscard:hover .newscardart img { transform: scale(1.03); }
.newscard:hover .newscardtitle { color: var(--blue); }
.newscardbody { padding: 12px 2px 0; display: flex; flex-direction: column; gap: 5px; }""")

sub(""".newstier.rest .newscardbody { padding: 12px 13px 14px; gap: 5px; }""",
    """.newstier.rest .newscardbody { padding: 10px 2px 0; gap: 4px; }""")

# ------------------------------------------------- the tiers stand apart
sub(""".newstier { display: grid; gap: 16px; margin-top: 24px; }""",
    """.newstier { display: grid; gap: 16px; margin-top: 24px; }
/* A change of rank, not a continuation. At the row gap the three tiers read
   as one grid that keeps changing its mind about how wide a card is. */
.newstier + .newstier { margin-top: 52px; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('picture, headline, date')
