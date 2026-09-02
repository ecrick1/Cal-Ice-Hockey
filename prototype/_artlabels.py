# -*- coding: utf-8 -*-
"""The small labels on a story stop shouting in a condensed face.

The tag, Share and More headlines were all set in Barlow Condensed,
uppercased, and letter-spaced two or three pixels apart. That treatment
belongs to a scoreboard and to the display type it sits beside; on a page of
prose it makes three small labels louder than the paragraphs they are
labelling, and RECAP in condensed capitals reads as a warning rather than a
category.

They take the body face at their written case, with the spacing normal.
Still small and still grey, so they stay labels - just ones that murmur.

Each gets a class of its own rather than an override on .eyebrow or .h6.
Those two are worn by dozens of things across the site and the whole console,
and half of them do want the scoreboard treatment; changing them here to fix
three labels on one page is how a rule ends up with six exceptions.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------ the tag on a story
sub("""        <p className="eyebrow" style={{ color: "var(--blue)" }}>{post.tag || "NEWS"}</p>""",
    """        <p className="artlabel arttag">{post.tag || "NEWS"}</p>""")

# ------------------------------------------------------------ More headlines
sub("""            <p className="h6" style={{ color: "var(--muted)", marginBottom: 14 }}>More headlines</p>""",
    """            <p className="artlabel" style={{ marginBottom: 14 }}>More headlines</p>""")

# -------------------------------------------------------------------- Share
sub("""      <p className="artsharelabel">Share</p>""",
    """      <p className="artlabel">Share</p>""")

sub(""".artsharelabel { margin: 0; font-family: var(--disp); font-weight: 600; font-size: 11px;
  letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); }""",
    """/* The small labels around a story: the tag, Share, More headlines.
   Body face, written case, ordinary spacing - a label beside prose should
   not be set like a scoreboard. */
.artlabel { margin: 0; font-family: var(--body); font-weight: 700; font-size: 13px;
  letter-spacing: 0; text-transform: none; color: var(--muted); }
/* The tag is the one that names the kind of story, so it keeps the navy. */
.arttag { color: var(--blue); }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('the labels murmur')
