# -*- coding: utf-8 -*-
"""Styles for the blocks and the two editors.

The public blocks borrow the site's own measurements rather than inventing
their own - the same section rhythm, the same card radius, the same gold
pill - so a built page reads as part of the site and not as something
generated into it.

The editors take the console's dark surfaces for the same reason.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------------ public blocks
sub("""/* Marks a link. A gold block behind the words read as highlighter pen, so""",
    """/* ---- Pages built from blocks ---- */
/* The hero carries an image when there is one and the navy when there is
   not, so a page with no picture is still a header rather than a gap. */
.pbhero { background: var(--deep); color: #fff; background-size: cover;
  background-position: center; padding-top: 64px; padding-bottom: 64px; position: relative; }
.pbhero::before { content: ""; position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(4,30,66,0.55), rgba(4,30,66,0.8)); }
.pbhero > * { position: relative; }
.pbeyebrow { margin: 0 0 10px; font-size: 11px; font-weight: 800; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--gold); }
.pbherotitle { color: #fff; margin: 0; }
.pbherblurb { margin: 12px 0 0; max-width: 60ch; font-size: 16px; line-height: 1.6;
  color: rgba(255,255,255,0.86); }

.pbcards { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px; margin-top: 18px; }
.pbcard { display: block; background: #fff; border: 1px solid var(--border); border-radius: 10px;
  padding: 20px; text-decoration: none; color: inherit; }
a.pbcard:hover { border-color: var(--rule-on); }
.pbcardtitle { margin: 0; font-weight: 800; font-size: 16px; color: var(--ink); }
.pbcardtext { margin: 8px 0 0; font-size: 14px; line-height: 1.6; color: var(--muted); }

.pbstats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 18px; background: var(--ice); border: 1px solid var(--border); border-radius: 10px;
  padding: 26px 20px; }
.pbstat { display: grid; justify-items: center; gap: 6px; text-align: center; }
.pbstatvalue { font-family: var(--disp); font-size: 38px; font-weight: 600; line-height: 1;
  color: var(--blue); }
.pbstatlabel { font-size: 12px; font-weight: 700; letter-spacing: 0.06em;
  text-transform: uppercase; color: var(--muted); }

.pbimage { display: block; width: 100%; border-radius: 10px; }
.pbcaption { margin: 10px 0 0; font-size: 13px; color: var(--muted); }

.pbcta { display: flex; align-items: center; gap: 20px; flex-wrap: wrap;
  background: var(--deep); border-radius: 12px; padding: 28px 30px; }
.pbctatitle { margin: 0; font-family: var(--disp); font-size: 27px; font-weight: 600;
  color: #fff; }
.pbctablurb { margin: 8px 0 0; font-size: 15px; color: rgba(255,255,255,0.8); max-width: 56ch; }
.pbcta .goldpill { margin-left: auto; }

.pbfaq { border-top: 1px solid var(--border); padding: 16px 0; }
.pbfaq summary { cursor: pointer; font-weight: 700; font-size: 16px; color: var(--ink);
  list-style: none; }
.pbfaq summary::-webkit-details-marker { display: none; }
.pbfaq summary::after { content: "+"; float: right; color: var(--muted); font-weight: 700; }
.pbfaq[open] summary::after { content: "\\u2212"; }
.pbfaq .legalbody { margin-top: 10px; }

/* Marks a link. A gold block behind the words read as highlighter pen, so""")

# ------------------------------------------------------------- the editors
sub(""".adminui .aupenwait { border-left: 3px solid var(--au-warn, #F5B544); }""",
    """.adminui .aupenwait { border-left: 3px solid var(--au-warn, #F5B544); }

/* ---- Page builder ---- */
.adminui .aublockhead { display: flex; align-items: flex-start; justify-content: space-between;
  gap: 12px; }
.adminui .aublockrow { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)) 30px;
  gap: 8px; align-items: center; margin-top: 8px; }
.adminui .aublockimg { display: block; max-width: 240px; border-radius: 8px; margin-bottom: 8px; }
.adminui .aublockpick { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px; }
.adminui .aublockopt { display: grid; gap: 3px; text-align: left; padding: 12px 14px;
  background: var(--au-raised); border: 1px solid var(--au-line); border-radius: 9px;
  cursor: pointer; color: inherit; font: inherit; }
.adminui .aublockopt:hover { border-color: var(--au-primary); }
.adminui .aublockoptname { font-size: 13.5px; font-weight: 700; color: var(--au-text); }
.adminui .aublockopthint { font-size: 11.5px; color: var(--au-faint); }

/* ---- Menu bar ---- */
.adminui .aunavlist { display: grid; gap: 6px; margin-top: 14px; }
.adminui .aunavrow { display: flex; align-items: center; gap: 6px; padding: 7px 9px;
  background: var(--au-raised); border: 1px solid var(--au-line); border-radius: 8px; }
.adminui .aunavrow.child { margin-left: 26px; background: none; }
.adminui .aunavrow.off { opacity: 0.5; }
.adminui .aunavlabel { flex: 1 1 auto; min-width: 0; padding: 4px 7px; font-size: 13px; }
.adminui .aunavwhat { flex: 0 0 auto; font-size: 10.5px; font-weight: 700; letter-spacing: 0.05em;
  text-transform: uppercase; color: var(--au-faint); }
.adminui .aunavrow .btn { flex: 0 0 auto; padding: 4px 8px; font-size: 12px; }
.adminui .aunavaddchild { margin: 4px 0 8px 26px; }
.adminui .aunavadd { border-color: var(--au-primary); }
/* The button that makes a page, last in its group and marked as an action
   rather than a destination. */
.adminui .aulink.aunewpage { color: var(--au-faint); }
.adminui .aulink.aunewpage:hover { color: var(--au-text); }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('styles in')
