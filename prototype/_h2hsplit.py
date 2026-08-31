# -*- coding: utf-8 -*-
"""Split the portrait away from the name so the row can fold.

A face and its name were one flex box, which meant the pair travelled
together and a phone had nowhere to put them but on their own line. As
separate cells the grid can do what the reference does: portraits and
figures across the top, the bar under them, the two names beneath that,
one at each edge.

Desktop gains the other half of the note - the visiting crest sits outside
its name now, mirroring ours, rather than tucked between the name and the
middle.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:120])
    s = s.replace(old, new)


# ------------------------------------------------------------------ markup
sub("""              <button className="h2hface" onClick={() => onPlayer(x.p.id)}>
                <PlayerAvatar size={38} photo={x.p.photo} />
                <span className="h2hnames">
                  <span className="h2hname">
                    <span className="h2hfirst">{splitName(x.p.name).first}</span>
                    <span className="h2hlast">{splitName(x.p.name).last}</span>
                  </span>
                  <span className="h2hpos">#{x.p.number || "\\u2014"} · {posOf(x.p)}</span>
                </span>
              </button>""",
    """              {/* The portrait duplicates the name's link, so it is out of the
                  tab order rather than a second stop at the same place. */}
              <button className="h2hpic" onClick={() => onPlayer(x.p.id)}
                tabIndex={-1} aria-hidden="true">
                <PlayerAvatar size={38} photo={x.p.photo} />
              </button>
              <button className="h2hwho" onClick={() => onPlayer(x.p.id)}>
                <span className="h2hname">
                  <span className="h2hfirst">{splitName(x.p.name).first}</span>
                  <span className="h2hlast">{splitName(x.p.name).last}</span>
                </span>
                <span className="h2hpos">#{x.p.number || "\\u2014"} · {posOf(x.p)}</span>
              </button>""")

sub("""              <span className="h2hface right">
                <span className="h2hnames">
                  <span className={"h2hname" + (THEIRS[label] ? "" : " unknown")}>
                    <span className="h2hfirst">{THEIRS[label] ? splitName(THEIRS[label].name).first : ""}</span>
                    <span className="h2hlast">
                      {THEIRS[label] ? splitName(THEIRS[label].name).last : "Not published"}
                    </span>
                  </span>
                  {/* Number and position, the same two facts as ours - their
                      games played is on the roster table, not here. */}
                  <span className="h2hpos">
                    {THEIRS[label]
                      ? [THEIRS[label].number ? "#" + THEIRS[label].number : null, THEIRS[label].pos]
                          .filter(Boolean).join(" · ")
                      : themName}
                  </span>
                </span>
                {game.opponentLogo
                  ? <img className="h2hmark" src={game.opponentLogo} alt="" />
                  : <OppBadge name={themName} size={38} />}
              </span>""",
    """              <span className="h2hpic right">
                {game.opponentLogo
                  ? <img className="h2hmark" src={game.opponentLogo} alt="" />
                  : <OppBadge name={themName} size={38} />}
              </span>
              <span className={"h2hwho right" + (THEIRS[label] ? "" : " unknown")}>
                <span className="h2hname">
                  <span className="h2hfirst">{THEIRS[label] ? splitName(THEIRS[label].name).first : ""}</span>
                  <span className="h2hlast">
                    {THEIRS[label] ? splitName(THEIRS[label].name).last : "Not published"}
                  </span>
                </span>
                {/* Number and position, the same two facts as ours - their
                    games played is on the roster table, not here. */}
                <span className="h2hpos">
                  {THEIRS[label]
                    ? [THEIRS[label].number ? "#" + THEIRS[label].number : null, THEIRS[label].pos]
                        .filter(Boolean).join(" · ")
                    : themName}
                </span>
              </span>""")

# --------------------------------------------------------------- desktop CSS
sub("""/* Face, number, category, number, face - the comparison reads inward to the
   middle rather than out at the two edges. */
.h2hbar { grid-template-columns: minmax(0, 1fr) auto minmax(74px, auto) auto minmax(0, 1fr);
  gap: 4px 14px; }
.h2hbar .gcbarlab { grid-column: 3; align-self: center; }
.h2hnum { font-family: var(--body); font-weight: 800; font-size: 28px; letter-spacing: -0.02em;
  color: var(--ink); font-variant-numeric: tabular-nums; line-height: 1; text-align: right; }
.h2hnum.right { text-align: left; }
.h2hbar .gcbartrack { grid-column: 1 / -1; margin-top: 10px; }
/* Nothing to divide, so no rail under it. */
.gcbar.norail { padding-bottom: 12px; }
.h2hface { display: flex; align-items: center; gap: 9px; background: none; border: 0;
  padding: 0; cursor: pointer; text-align: left; min-width: 0; grid-row: 1; }
.h2hface.right { flex-direction: row-reverse; text-align: right; cursor: default;
  grid-column: 5; }
.h2hface.right .h2hnames { align-items: flex-end; }
.h2hmark { width: 38px; height: 38px; object-fit: contain; flex: 0 0 auto; }
.h2hnames { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.h2hname { display: flex; flex-direction: column; line-height: 1.2; min-width: 0; }
.h2hfirst { font-size: 12px; font-weight: 500; color: var(--muted); }
.h2hlast { font-size: 14.5px; font-weight: 800; color: var(--ink);
  overflow: hidden; text-overflow: ellipsis; }
.h2hface.right .h2hname { align-items: flex-end; }
.h2hname.unknown .h2hlast { color: var(--muted); font-weight: 700; }
button.h2hface:hover .h2hlast { color: var(--blue); }
.h2hpos { font-size: 11px; font-weight: 600; color: var(--muted); white-space: nowrap; }""",
    """/* Portrait, name, figure, category, figure, name, crest. Each side reads
   outward from the middle, so the two marks bookend the row. */
.h2hbar { grid-template-columns:
  auto minmax(0, 1fr) auto minmax(74px, auto) auto minmax(0, 1fr) auto;
  gap: 4px 12px; align-items: center; }
.h2hbar > .h2hpic { grid-area: 1 / 1 / 2 / 2; }
.h2hbar > .h2hwho { grid-area: 1 / 2 / 2 / 3; }
.h2hbar > .h2hnum { grid-area: 1 / 3 / 2 / 4; }
.h2hbar > .gcbarlab { grid-area: 1 / 4 / 2 / 5; }
.h2hbar > .h2hnum.right { grid-area: 1 / 5 / 2 / 6; }
.h2hbar > .h2hwho.right { grid-area: 1 / 6 / 2 / 7; }
.h2hbar > .h2hpic.right { grid-area: 1 / 7 / 2 / 8; }
.h2hbar > .gcbartrack { grid-area: 2 / 1 / 3 / 8; margin-top: 10px; }
.h2hnum { font-family: var(--body); font-weight: 800; font-size: 28px; letter-spacing: -0.02em;
  color: var(--ink); font-variant-numeric: tabular-nums; line-height: 1; text-align: right; }
.h2hnum.right { text-align: left; }
/* Nothing to divide, so no rail under it. */
.gcbar.norail { padding-bottom: 12px; }
.h2hpic { display: flex; align-items: center; background: none; border: 0; padding: 0;
  cursor: pointer; }
.h2hpic.right { cursor: default; }
.h2hmark { width: 38px; height: 38px; object-fit: contain; flex: 0 0 auto; }
.h2hwho { display: flex; flex-direction: column; gap: 1px; min-width: 0; background: none;
  border: 0; padding: 0; cursor: pointer; text-align: left; align-items: flex-start; }
.h2hwho.right { cursor: default; text-align: right; align-items: flex-end; }
.h2hname { display: flex; flex-direction: column; line-height: 1.2; min-width: 0;
  max-width: 100%; }
.h2hfirst { font-size: 12px; font-weight: 500; color: var(--muted); }
.h2hlast { font-size: 14.5px; font-weight: 800; color: var(--ink);
  overflow: hidden; text-overflow: ellipsis; }
.h2hwho.unknown .h2hlast { color: var(--muted); font-weight: 700; }
button.h2hwho:hover .h2hlast, .h2hpic:hover + .h2hwho .h2hlast { color: var(--blue); }
.h2hpos { font-size: 11px; font-weight: 600; color: var(--muted); white-space: nowrap; }""")

# ---------------------------------------------------------------- mobile CSS
sub("""@media (max-width: 620px) {
  /* Two columns: who on the left, their figure on the right, one line a
     side. Placed by hand - auto-flow put the visitor's number a row above
     the name it belongs to. */
  .h2hbar { grid-template-columns: minmax(0, 1fr) auto; gap: 8px 12px;
    align-items: center; }
  .h2hbar > .gcbarlab { grid-area: 1 / 1 / 2 / 3; text-align: left;
    font-size: 12px; font-weight: 800; color: var(--ink); }
  .h2hbar > .h2hface { grid-area: 2 / 1 / 3 / 2; }
  .h2hbar > .h2hnum { grid-area: 2 / 2 / 3 / 3; }
  .h2hbar > .h2hface.right { grid-area: 3 / 1 / 4 / 2; }
  .h2hbar > .h2hnum.right { grid-area: 3 / 2 / 4 / 3; }
  .h2hbar > .gcbartrack { grid-area: 4 / 1 / 5 / 3; margin-top: 4px; }
  /* Mirroring the visitor's block only made sense opposite ours. The mark
     comes after the name in the markup, so reversing puts it in front and
     flex-end packs the pair back against the left edge. */
  .h2hbar > .h2hface.right { flex-direction: row-reverse; justify-content: flex-end;
    text-align: left; }
  .h2hbar > .h2hface.right .h2hnames { align-items: flex-start; }
  .h2hnum, .h2hnum.right { text-align: right; font-size: 24px; }
  /* Kept, small: with the two sides stacked rather than opposite, the
     crest is the only thing saying which line belongs to whom. */
  .h2hmark { width: 26px; height: 26px; }
  .h2hface > img, .h2hface > svg { width: 26px !important; height: 26px !important; }
  .h2hname { font-size: 12.5px; }
  .h2hpos { white-space: normal; }
}""",
    """@media (max-width: 620px) {
  /* The names will not fit beside the figures at this width, so they drop
     under the bar - portraits and figures on top, the split beneath them,
     a name at each edge below that. */
  .h2hbar { grid-template-columns: auto minmax(0, 1fr) auto minmax(0, 1fr) auto;
    gap: 6px 8px; align-items: center; }
  .h2hbar > .h2hpic { grid-area: 1 / 1 / 2 / 2; }
  .h2hbar > .h2hnum { grid-area: 1 / 2 / 2 / 3; text-align: center; }
  .h2hbar > .gcbarlab { grid-area: 1 / 3 / 2 / 4; }
  .h2hbar > .h2hnum.right { grid-area: 1 / 4 / 2 / 5; text-align: center; }
  .h2hbar > .h2hpic.right { grid-area: 1 / 5 / 2 / 6; }
  .h2hbar > .gcbartrack { grid-area: 2 / 1 / 3 / 6; margin-top: 8px; }
  .h2hbar > .h2hwho { grid-area: 3 / 1 / 4 / 4; }
  .h2hbar > .h2hwho.right { grid-area: 3 / 4 / 4 / 6; }
  .h2hnum, .h2hnum.right { font-size: 26px; }
  .h2hpos { white-space: normal; }
}""")

io.open(p, 'w', encoding='utf-8').write(s)
print('row flattened')
