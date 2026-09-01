# -*- coding: utf-8 -*-
"""Open the strip on what is still to come, and take the odds back off.

The strip already scrolled to the next game. It just could not get there:
with five finals and one fixture left, putting that fixture at the left
edge would need more content to its right than exists, so the browser
clamped the scroll and the band opened on games already played.

A tail spacer fixes it. It is measured, not guessed - exactly the width
needed for the first upcoming game to reach the left edge, and zero when
there is already enough after it, which is most of a season. Past games
stay in the strip and stay one arrow to the left.

Two things follow. The measurement is redone when the crests finish
loading, because they change the widths it was based on, and when the
window resizes. And the arrows now go dim at the ends, so the new empty
space at the right of a nearly-finished season does not read as somewhere
still to go.

The odds line comes off head to head, and its two functions with it rather
than left behind as something nothing calls.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------------- the odds, out
sub("""  /* The one line on this card that is a claim rather than a record. */
  const odds = opp.data ? matchupOdds(us, opp.data, game.homeAway) : null;
  const COMPARE_ROWS = opp.data ? [""",
    """  const COMPARE_ROWS = opp.data ? [""")

sub("""    ...(odds == null ? [] : [["Odds", Math.round(odds * 100) + "%",
      Math.round((1 - odds) * 100) + "%", true]]),
""", "")

sub("""            {odds != null && (
              <p className="bsm gcnone gpnote gcoddsnote">
                Odds are from goals for and against on both sides, weighted for how
                much of each season has been played and for
                {game.homeAway === "H" ? " home ice" : game.homeAway === "A" ? " playing away" : " a neutral rink"}.
                Neither record is adjusted for who they played.
              </p>
            )}
""", "")

sub("""/* The footnote that keeps the one estimated line honest. */
.gcoddsnote { margin-top: 16px; }
""", "")

# The two functions go with it; nothing else calls them.
i = s.index("""/**
 * Win expectation from goals for and against, pulled toward even by how""")
j = s.index("function seasonRecord(season) {")
s = s[:i] + s[j:]

# ------------------------------------------------------------ the strip
sub("""  const anchorRef = useRef(null);

  useEffect(() => {
    const row = rowRef.current;
    const anchor = anchorRef.current;
    if (!row || !anchor) return;
    const delta = anchor.getBoundingClientRect().left - row.getBoundingClientRect().left;
    row.scrollLeft += delta - 8;
  }, [anchorId]);

  const scroll = (dir) => {
    if (rowRef.current) rowRef.current.scrollBy({ left: dir * 360, behavior: "smooth" });
  };""",
    """  const anchorRef = useRef(null);
  const tailRef = useRef(null);
  const [ends, setEnds] = useState({ start: true, end: false });

  const readEnds = useCallback(() => {
    const row = rowRef.current;
    if (!row) return;
    const max = row.scrollWidth - row.clientWidth;
    setEnds({ start: row.scrollLeft <= 2, end: row.scrollLeft >= max - 2 });
  }, []);

  /* Put the anchor at the left edge, and give the strip enough tail to get
     there. Late in a season the games still to come do not fill the band, so
     without this the scroll clamps and the strip opens on finals - which is
     the one thing it is not for. */
  const fit = useCallback(() => {
    const row = rowRef.current;
    const anchor = anchorRef.current;
    const tail = tailRef.current;
    if (!row || !anchor) return;
    if (tail) tail.style.width = "0px";
    const at = anchor.getBoundingClientRect().left - row.getBoundingClientRect().left
      + row.scrollLeft;
    if (tail) {
      const after = row.scrollWidth - at;
      tail.style.width = Math.max(0, Math.ceil(row.clientWidth - after)) + "px";
    }
    row.scrollLeft = Math.max(0, at - 8);
    readEnds();
  }, [readEnds]);

  useEffect(() => {
    fit();
    /* The crests arrive after the first paint and change every width this
       was measured from. */
    const row = rowRef.current;
    const imgs = row ? [...row.querySelectorAll("img")].filter((i) => !i.complete) : [];
    imgs.forEach((i) => i.addEventListener("load", fit, { once: true }));
    window.addEventListener("resize", fit);
    return () => {
      imgs.forEach((i) => i.removeEventListener("load", fit));
      window.removeEventListener("resize", fit);
    };
  }, [anchorId, fit]);

  const scroll = (dir) => {
    if (rowRef.current) rowRef.current.scrollBy({ left: dir * 360, behavior: "smooth" });
  };""")

sub("""        <button className="chev" aria-label="Previous games" onClick={() => scroll(-1)}><IcChevL size={22} /></button>
        <div className="sboard-row" ref={rowRef}>""",
    """        <button className="chev" aria-label="Previous games" disabled={ends.start}
          onClick={() => scroll(-1)}><IcChevL size={22} /></button>
        <div className="sboard-row" ref={rowRef} onScroll={readEnds}>""")

sub("""        </div>
        <button className="chev" aria-label="More games" onClick={() => scroll(1)}><IcChevR size={22} /></button>""",
    """          <span className="sboard-tail" ref={tailRef} aria-hidden="true" />
        </div>
        <button className="chev" aria-label="More games" disabled={ends.end}
          onClick={() => scroll(1)}><IcChevR size={22} /></button>""")

# The spacer is inert: no width of its own until fit() measures one.
sub(""".sboard-row { display: flex; gap: 12px; overflow-x: auto; scroll-behavior: smooth;""",
    """/* Measured by fit(): the room the first upcoming game needs to reach the
   left edge when the games after it do not fill the band. */
.sboard-tail { flex: 0 0 auto; width: 0; align-self: stretch; }
.chev:disabled { opacity: 0.25; cursor: default; }
.sboard-row { display: flex; gap: 12px; overflow-x: auto; scroll-behavior: smooth;""")

io.open(p, 'w', encoding='utf-8').write(s)
print('strip opens on upcoming; odds removed')
