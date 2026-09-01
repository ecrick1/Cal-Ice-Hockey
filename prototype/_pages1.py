# -*- coding: utf-8 -*-
"""Pages built from blocks, and a nav that is data rather than markup.

Every public page so far has been a component with its own name in a switch,
which is right for the ones that render the schedule or a player's season -
those pages are the data. It is wrong for a page that is words and pictures
and a link at the bottom, because writing one meant writing a component.

So a page can now be a list of blocks. Seven of them, each matching
something the site already does: a hero, prose, a row of cards, a band of
figures, a picture, a call to action, and a set of questions that open. They
reuse the classes the rest of the site is built from rather than inventing a
second visual language underneath the first.

Blocks are stored, not compiled, and a block whose type nothing recognises
is skipped rather than throwing - a page saved by a newer version of the
console should degrade to the parts this one understands.

The nav becomes data at the same time, because a page nobody can navigate to
is not much of a page. The default is exactly the bar as it was written, so
nothing moves until somebody moves it - and the dropdowns keep the tuple
shape NavMenu already took, so the menu component is untouched.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ===================================================== the model + renderer
sub("""/* The Team submenu, in one place: the desktop dropdown and the mobile
   accordion read the same list so they cannot drift apart. */
const NAV_TEAM = [""",
    """/* ---------------- Pages built from blocks ----------------
 *
 * A page that is words and pictures rather than a view of the data. Each
 * block names a shape the site already has, so a built page looks like the
 * rest of the site instead of like a page builder.
 *
 * `fields` drives the editor; the renderer reads the same names. Adding a
 * block type means adding one entry here and one case in PageBlock.
 */
const BLOCK_TYPES = [
  ["hero", "Hero", "A title over the width of the page",
    [["eyebrow", "Eyebrow", "line"], ["title", "Title", "line"],
     ["blurb", "Blurb", "text"], ["image", "Background image", "image"]]],
  ["rich", "Text", "Paragraphs, headings and lists",
    [["title", "Heading", "line"], ["body", "Body", "markdown"]]],
  ["cards", "Cards", "A row of linked cards",
    [["title", "Heading", "line"],
     ["items", "Cards", "list", [["title", "Title"], ["text", "Text"], ["href", "Link"]]]]],
  ["stats", "Figures", "A band of numbers",
    [["items", "Figures", "list", [["value", "Figure"], ["label", "Label"]]]]],
  ["image", "Picture", "One image with a caption",
    [["image", "Image", "image"], ["caption", "Caption", "line"]]],
  ["cta", "Call to action", "A band with a button",
    [["title", "Title", "line"], ["blurb", "Blurb", "text"],
     ["label", "Button", "line"], ["href", "Link", "line"]]],
  ["faq", "Questions", "Questions that open",
    [["title", "Heading", "line"],
     ["items", "Questions", "list", [["q", "Question"], ["a", "Answer"]]]]],
];
const blockType = (t) => BLOCK_TYPES.find((b) => b[0] === t) || null;

/* Rows a repeating block actually has something in - an empty row is one
   somebody started and left, not content. */
const filled = (items, keys) => (items || [])
  .filter((it) => it && keys.some((k) => String(it[k] || "").trim()));

function PageBlock({ block, goto }) {
  const b = block || {};
  const has = (k) => String(b[k] || "").trim();

  if (b.type === "hero") {
    return (
      <section className="section pbhero"
        style={b.image ? { backgroundImage: `url(${b.image})` } : undefined}>
        <div className="wrap" style={{ maxWidth: 900 }}>
          {has("eyebrow") && <p className="pbeyebrow">{b.eyebrow}</p>}
          {has("title") && <h1 className="stitle pbherotitle">{b.title}</h1>}
          {has("blurb") && <p className="pbherblurb">{b.blurb}</p>}
        </div>
      </section>
    );
  }

  if (b.type === "rich") {
    return (
      <section className="section">
        <div className="wrap" style={{ maxWidth: 760 }}>
          {has("title") && <h2 className="stitle">{b.title}</h2>}
          {has("body") && <div className="prose"><Markdown text={b.body} /></div>}
        </div>
      </section>
    );
  }

  if (b.type === "cards") {
    const items = filled(b.items, ["title", "text"]);
    if (!items.length) return null;
    return (
      <section className="section">
        <div className="wrap">
          {has("title") && <h2 className="stitle">{b.title}</h2>}
          <div className="pbcards">
            {items.map((it, i) => {
              const inner = (
                <>
                  <p className="pbcardtitle">{it.title}</p>
                  {it.text && <p className="pbcardtext">{it.text}</p>}
                </>
              );
              return it.href
                ? <a className="pbcard" key={i} href={it.href}
                    target={/^https?:/.test(it.href) ? "_blank" : undefined}
                    rel="noreferrer noopener">{inner}</a>
                : <div className="pbcard" key={i}>{inner}</div>;
            })}
          </div>
        </div>
      </section>
    );
  }

  if (b.type === "stats") {
    const items = filled(b.items, ["value", "label"]);
    if (!items.length) return null;
    return (
      <section className="section">
        <div className="wrap">
          <div className="pbstats">
            {items.map((it, i) => (
              <div className="pbstat" key={i}>
                <span className="pbstatvalue">{it.value}</span>
                <span className="pbstatlabel">{it.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (b.type === "image") {
    if (!has("image")) return null;
    return (
      <section className="section">
        <div className="wrap" style={{ maxWidth: 900 }}>
          <img className="pbimage" src={b.image} alt={b.caption || ""} />
          {has("caption") && <p className="pbcaption">{b.caption}</p>}
        </div>
      </section>
    );
  }

  if (b.type === "cta") {
    if (!has("title") && !has("label")) return null;
    return (
      <section className="section">
        <div className="wrap">
          <div className="pbcta">
            <div>
              {has("title") && <p className="pbctatitle">{b.title}</p>}
              {has("blurb") && <p className="pbctablurb">{b.blurb}</p>}
            </div>
            {has("label") && has("href") && (
              <a className="goldpill" href={b.href}
                target={/^https?:/.test(b.href) ? "_blank" : undefined}
                rel="noreferrer noopener">{b.label}</a>
            )}
          </div>
        </div>
      </section>
    );
  }

  if (b.type === "faq") {
    const items = filled(b.items, ["q", "a"]);
    if (!items.length) return null;
    return (
      <section className="section">
        <div className="wrap" style={{ maxWidth: 760 }}>
          {has("title") && <h2 className="stitle">{b.title}</h2>}
          {items.map((it, i) => (
            <details className="pbfaq" key={i}>
              <summary>{it.q}</summary>
              <div className="prose"><Markdown text={it.a || ""} /></div>
            </details>
          ))}
        </div>
      </section>
    );
  }

  /* A type this build does not know. Skipped rather than thrown, so a page
     written by a newer console still shows the parts this one understands. */
  return null;
}

function CustomPage({ page, goto }) {
  if (!page) return null;
  const blocks = (page.blocks || []).filter((b) => b && blockType(b.type));
  return (
    <main style={{ background: "var(--page)", minHeight: "50vh" }}>
      {blocks.length ? blocks.map((b) => <PageBlock key={b.id} block={b} goto={goto} />) : (
        <section className="section" style={{ paddingTop: 40 }}>
          <div className="wrap" style={{ maxWidth: 900 }}>
            <h1 className="stitle">{page.title || "Untitled"}</h1>
            <div className="emptybox">
              <p style={{ margin: 0, fontWeight: 700, color: "var(--ink)" }}>Nothing here yet</p>
              <p className="bsm" style={{ margin: "6px 0 0", color: "var(--muted)" }}>
                This page has no blocks on it. Add some in the console.
              </p>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}

/* The Team submenu, in one place: the desktop dropdown and the mobile
   accordion read the same list so they cannot drift apart. */
const NAV_TEAM = [""")

io.open(p, 'w', encoding='utf-8').write(s)
print('blocks and the page renderer')
