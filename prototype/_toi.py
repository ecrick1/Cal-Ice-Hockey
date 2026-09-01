# -*- coding: utf-8 -*-
"""Time on ice is counted, not typed, and the columns share the width evenly.

TOI was whatever somebody had typed into the minutes field, which meant a
game being scored right now showed a dash for the man who had been in net
for the whole first period. The number was only ever right for a game
finished and written up afterwards, which is the one case where it matters
least.

It is counted off the same timeline the goals-against split already uses:
the keeper who started, each change, each pull, each return, and the clock
running underneath. A live game measures to the current second and moves
with it; a finished one measures to the end of the last period played, or to
the goal that ended it in overtime, because sudden death stops the clock
where it stops.

A typed figure still stands where nothing can be counted - two keepers in a
game whose changes were never recorded is exactly the case the split cannot
answer either, and 48 and 13 typed off a scoresheet beat two dashes.

And the columns divide what is left of the width equally instead of each
sizing to its own contents, so ten numbers do not arrive in ten different
widths. The number and name stay pinned as they were, since that is what
holds the three tables in line with each other.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ===================================================== how long the game is
sub("""/* Minutes as a scoreboard writes them. The field is a number because it is
   typed as one; 40.5 is forty minutes and thirty seconds. */
function fmtTOI(v) {
  const m = Number(v);
  if (!m) return "\\u2014";
  const whole = Math.floor(m);
  const secs = Math.round((m - whole) * 60);
  return whole + ":" + String(secs).padStart(2, "0");
}""",
    """/**
 * Seconds of hockey played so far, from the opening face-off.
 *
 * A game still being played has run as long as its clock says. A finished one
 * ran to the end of the last period anybody recorded a play in - except in
 * overtime, which is sudden death and stops on the goal that ends it.
 *
 * Floored at three periods for a finished game, because a sparse log is not
 * evidence that the third period was never played.
 */
function gameSeconds(game, plays, live, now) {
  if (!game.result) return elapsedSecs(live || game.live || {}, now);
  const order = ["1", "2", "3", "OT"];
  const otGoal = (plays || []).find((x) => x.kind === "goal" && x.period === "OT");
  if (otGoal) return playElapsed(otGoal);
  const seen = (plays || [])
    .map((x) => order.indexOf(String(x.period || "1"))).filter((i) => i >= 0);
  const idx = Math.max(2, seen.length ? Math.max(...seen) : 2);
  return order.slice(0, idx + 1).reduce((n, k) => n + periodSecs(k), 0);
}

/**
 * How long each goaltender was actually in net, in seconds.
 *
 * The same timeline the goals-against split is read from: who started, then
 * every change, pull and return, measured against the clock. A pulled net
 * belongs to nobody, so those seconds are charged to no one.
 *
 * Returns null when there is nothing to count from - no changes recorded and
 * more than one keeper with a line - which is where a typed figure is the
 * better answer and the only one there is.
 */
function goalieTOI(rows, plays, mine, endAt) {
  const changes = (plays || [])
    .filter((x) => x.kind === "goalie" && x.team === (mine ? "us" : "them"))
    .sort((a, b) => playElapsed(a) - playElapsed(b));
  const played = rows.filter((r) => Number(r.l.saves) || Number(r.l.ga) || Number(r.l.minutes));
  if (!changes.length) {
    return played.length === 1 ? { [played[0].id]: Math.max(0, endAt) } : null;
  }
  const byName = new Map(rows.map((r) => [String(r.name || "").toLowerCase(), r.id]));
  const out = {};
  let who = changes[0].out || (played[0] || {}).name || "";
  let since = 0;
  const close = (name, until) => {
    const id = byName.get(String(name || "").toLowerCase());
    if (id) out[id] = (out[id] || 0) + Math.max(0, Math.min(until, endAt) - since);
  };
  for (const c of changes) {
    const t = playElapsed(c);
    close(who, t);
    since = t;
    /* An empty net is nobody's time. */
    who = c.phase === "pulled" ? "" : (c.player || "");
  }
  close(who, endAt);
  return out;
}

/* Seconds as a scoreboard writes them. */
function fmtMMSS(secs) {
  const t = Math.max(0, Math.round(Number(secs) || 0));
  return Math.floor(t / 60) + ":" + String(t % 60).padStart(2, "0");
}

/* The typed field is a number of minutes, because that is how a scoresheet
   writes it; 40.5 is forty minutes and thirty seconds. */
function fmtTOI(v) {
  const m = Number(v);
  if (!m) return "\\u2014";
  return fmtMMSS(m * 60);
}""")

# ============================================================== the table
sub("""function GoalieTable({ rows, onPlayer, plays, mine }) {
  if (!rows.length) return null;
  const split = goalieGaSplit(rows, plays, mine);""",
    """function GoalieTable({ rows, onPlayer, plays, mine, endAt }) {
  if (!rows.length) return null;
  const split = goalieGaSplit(rows, plays, mine);
  /* Counted where it can be counted; the typed figure where it cannot. */
  const toi = endAt == null ? null : goalieTOI(rows, plays, mine, endAt);""")

sub("""        <table className="stats gcbt">
          <thead>
            <tr><StatTh label="#" /><th>Goaltender</th>""",
    """        <table className="stats gcbt gcbtgk">
          <thead>
            <tr><StatTh label="#" /><th>Goaltender</th>""")

sub("""                  <td>{fmtTOI(r.l.minutes)}</td>""",
    """                  <td>{toi && toi[r.id] != null ? fmtMMSS(toi[r.id]) : fmtTOI(r.l.minutes)}</td>""")

sub("""                }))} onPlayer={onPlayer} plays={plays} mine />""",
    """                }))} onPlayer={onPlayer} plays={plays} mine endAt={playedSecs} />""")

sub("""                }))} plays={plays} />""",
    """                }))} plays={plays} endAt={playedSecs} />""")

sub("""  const shotTally = (() => {""",
    """  /* How much hockey has been played, for the goaltenders' time on ice. It
     moves with the clock during a live game. */
  const playedSecs = gameSeconds(game, plays, game.live, now);

  const shotTally = (() => {""")

# ------------------------------------------------------------------- CSS
sub(""".gcbt { width: 100%; }
.gcbt th:nth-child(1), .gcbt td:nth-child(1) { width: 46px; }
.gcbt th:nth-child(2), .gcbt td:nth-child(2) { width: 210px; }
.gcbt th:nth-child(3), .gcbt td:nth-child(3) { width: 52px; }""",
    """/* Fixed layout so the figures divide what is left of the width equally
   rather than each column sizing to its own contents - ten numbers arriving
   in ten different widths is what made this read as a list rather than a
   table. Number and name stay pinned, which is what holds the three tables
   in line with one another. */
.gcbt { width: 100%; table-layout: fixed; min-width: 620px; }
.gcbt th:nth-child(1), .gcbt td:nth-child(1) { width: 46px; }
.gcbt th:nth-child(2), .gcbt td:nth-child(2) { width: 200px; }
.gcbt th, .gcbt td { overflow: hidden; text-overflow: ellipsis; }
/* Only the skaters have a position column to line up. */
.gcbt:not(.gcbtgk) th:nth-child(3), .gcbt:not(.gcbtgk) td:nth-child(3) { width: 52px; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('time on ice is counted; the columns share the width')
