"""Donate moves into the More menu; the mobile CTA pair gets a real layout."""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:100])
    s = s.replace(old, new)


# --------------------------------------------- NavMenu: allow a link item
sub("""          {items.map(([k, text]) => (
            <button key={k} role="menuitem" className={"navdropitem " + (view === k ? "on" : "")}
              onClick={() => { setView(k); setOpen(false); }}>
              {text}
            </button>
          ))}""",
    """          {/* A third element makes the item a link out rather than a view. */}
          {items.map(([k, text, href]) => (href ? (
            <a key={k} role="menuitem" className="navdropitem" href={href}
              target="_blank" rel="noreferrer noopener" onClick={() => setOpen(false)}>
              {text}
            </a>
          ) : (
            <button key={k} role="menuitem" className={"navdropitem " + (view === k ? "on" : "")}
              onClick={() => { setView(k); setOpen(false); }}>
              {text}
            </button>
          )))}""")

# ---------------------------------------- desktop: drop the pill, add item
sub("""            {donateUrl && (
              <a className="navlink navcta donate" href={donateUrl} target="_blank" rel="noreferrer noopener">
                Donate
              </a>
            )}
""", "")

sub("""            <NavMenu label="More" view={view} setView={setView} items={NAV_MORE} />""",
    """            <NavMenu label="More" view={view} setView={setView} items={moreItems} />""")

# ------------------------------------------ mobile: drop the pill, add item
sub("""              {donateUrl && (
                <a className="goldpill ghost" href={donateUrl} target="_blank" rel="noreferrer noopener"
                  onClick={() => setNavOpen(false)}>Donate</a>
              )}
""", "")

sub("""                {NAV_MORE.map(([k, text]) => (
                  <button key={k} className={"navpanelitem child" + (view === k ? " on" : "")}
                    onClick={() => goNav(k)}>{text}</button>
                ))}""",
    """                {moreItems.map(([k, text, href]) => (href ? (
                  <a key={k} className="navpanelitem child" href={href}
                    target="_blank" rel="noreferrer noopener"
                    onClick={() => setNavOpen(false)}>{text}</a>
                ) : (
                  <button key={k} className={"navpanelitem child" + (view === k ? " on" : "")}
                    onClick={() => goNav(k)}>{text}</button>
                )))}""")

sub("""                + (NAV_MORE.some(([k]) => k === view) ? " on" : "")}""",
    """                + (NAV_MORE.some(([k]) => k === view) ? " on" : "")}""")

# ------------------------------------------------------- the merged list
sub("""  const donateUrl = ((site && site.settings) || {}).donateUrl || "";""",
    """  const donateUrl = ((site && site.settings) || {}).donateUrl || "";
  /* Giving is a link out, so it joins the menu rather than the view list. */
  const moreItems = donateUrl ? [...NAV_MORE, ["donate", "Donate", donateUrl]] : NAV_MORE;""")

# -------------------------------------------------------- CSS: the pills
sub(""".navpanelcta { display: flex; gap: 8px; padding: 14px 24px 18px;
  border-top: 1px solid rgba(255,255,255,0.09); }""",
    """/* Two equal buttons filling the row. As loose pills they floated under a
   stack of full-width rows and read as an afterthought. */
.navpanelcta { display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
  padding: 18px 24px 22px; border-top: 1px solid rgba(255,255,255,0.09); }
.navpanelcta .goldpill { padding: 13px 14px; text-align: center; font-size: 15px;
  font-weight: 800; }""")

# The donate pill styling is no longer used anywhere.
sub("""/* No display rule here: the breakpoint below hides every .navcta, and setting
   one would keep this pill in a header that has no room for it - on a phone it
   lives in the menu panel instead. */
.navcta.donate { background: transparent; color: #fff; box-shadow: inset 0 0 0 1.5px rgba(255,255,255,0.45);
  text-decoration: none; align-items: center; line-height: 1; }
.navcta.donate:hover { background: rgba(255,255,255,0.1); color: #fff; }
/* The only ghost pill sits in the mobile menu panel, which is navy - so it
   is outlined in white, not in the ink colour the gold pills use. */
.goldpill.ghost { background: transparent; color: #fff;
  box-shadow: inset 0 0 0 1.5px rgba(255,255,255,0.45); }
.goldpill.ghost:hover { background: rgba(255,255,255,0.1); color: #fff; }
""", "")

# A link in the drop needs the same box a button gets.
sub(""".navdropitem""", """.navdropitem""", s.count(".navdropitem"))

io.open(p, 'w', encoding='utf-8').write(s)
print('done')
