# -*- coding: utf-8 -*-
"""One measure down a built page, instead of three.

The blocks each chose their own width - the hero 900, prose 760, cards and
figures the full 1160 - so the left edge of the page moved every time the
block type changed. The hero title started 125 pixels in, the heading under
it 160, and the cards below that 30. Nothing lined up with anything, which
is what reads as squished: the content is not narrow, it is ragged.

Every block sits in the same wrap now, so there is one left edge the whole
way down. Prose is still held to a readable line - about 68 characters -
but by constraining the text rather than the column, so a paragraph stops
where a paragraph should and still starts where everything else does.

The hero also stops borrowing the section heading's style. That style is a
navy rule beside dark text, which on a navy hero is an invisible bar in
front of white text - it is a page title, not a section heading, and it now
has the size to say so.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------- one wrap for every block
sub("""      <section className="section pbhero"
        style={b.image ? { backgroundImage: `url(${b.image})` } : undefined}>
        <div className="wrap" style={{ maxWidth: 900 }}>
          {has("eyebrow") && <p className="pbeyebrow">{b.eyebrow}</p>}
          {has("title") && <h1 className="stitle pbherotitle">{b.title}</h1>}
          {has("blurb") && <p className="pbherblurb">{b.blurb}</p>}
        </div>
      </section>""",
    """      <section className="section pbhero"
        style={b.image ? { backgroundImage: `url(${b.image})` } : undefined}>
        <div className="wrap">
          {has("eyebrow") && <p className="pbeyebrow">{b.eyebrow}</p>}
          {has("title") && <h1 className="pbherotitle">{b.title}</h1>}
          {has("blurb") && <p className="pbherblurb">{b.blurb}</p>}
        </div>
      </section>""")

sub("""        <div className="wrap" style={{ maxWidth: 760 }}>
          {has("title") && <h2 className="stitle">{b.title}</h2>}
          {has("body") && <div className="legalbody">{renderArticle(b.body, goto || (() => {}))}</div>}
        </div>""",
    """        <div className="wrap">
          {has("title") && <h2 className="stitle">{b.title}</h2>}
          {has("body") && (
            <div className="legalbody pbprose">{renderArticle(b.body, goto || (() => {}))}</div>
          )}
        </div>""")

sub("""        <div className="wrap" style={{ maxWidth: 900 }}>
          <img className="pbimage" src={b.image} alt={b.caption || ""} />
          {has("caption") && <p className="pbcaption">{b.caption}</p>}
        </div>""",
    """        <div className="wrap">
          <img className="pbimage" src={b.image} alt={b.caption || ""} />
          {has("caption") && <p className="pbcaption">{b.caption}</p>}
        </div>""")

sub("""        <div className="wrap" style={{ maxWidth: 760 }}>
          {has("title") && <h2 className="stitle">{b.title}</h2>}
          {items.map((it, i) => (
            <details className="pbfaq" key={i}>""",
    """        <div className="wrap pbprose">
          {has("title") && <h2 className="stitle">{b.title}</h2>}
          {items.map((it, i) => (
            <details className="pbfaq" key={i}>""")

sub("""      {blocks.length ? blocks.map((b) => <PageBlock key={b.id} block={b} goto={goto} />) : (
        <section className="section" style={{ paddingTop: 40 }}>
          <div className="wrap" style={{ maxWidth: 900 }}>""",
    """      {blocks.length ? blocks.map((b) => <PageBlock key={b.id} block={b} goto={goto} />) : (
        <section className="section" style={{ paddingTop: 40 }}>
          <div className="wrap">""")

# ------------------------------------------------------------------- CSS
sub(""".pbherotitle { color: #fff; margin: 0; }""",
    """/* A page title, not a section heading. The heading style is a navy rule
   beside dark text, which on a navy hero is an invisible bar in front of
   white type. */
.pbherotitle { margin: 0; color: #fff; font-family: var(--body); font-weight: 800;
  font-size: clamp(2rem, 5vw, 3.1rem); line-height: 1.05; letter-spacing: -0.01em; }""")

sub(""".pbherblurb { margin: 12px 0 0; max-width: 60ch; font-size: 16px; line-height: 1.6;
  color: rgba(255,255,255,0.86); }""",
    """.pbherblurb { margin: 14px 0 0; max-width: 60ch; font-size: 17px; line-height: 1.6;
  color: rgba(255,255,255,0.86); }
/* Prose is held to a readable line by narrowing the text, not the column, so
   a paragraph ends where a paragraph should and still begins where every
   other block on the page begins. */
.pbprose > * { max-width: 68ch; }""")

sub(""".pbhero { background: var(--deep); color: #fff; background-size: cover;
  background-position: center; padding-top: 64px; padding-bottom: 64px; position: relative; }""",
    """.pbhero { background: var(--deep); color: #fff; background-size: cover;
  background-position: center; position: relative; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('one measure down the page')
