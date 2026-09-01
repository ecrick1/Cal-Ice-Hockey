# -*- coding: utf-8 -*-
"""Our sheet becomes the same sheet, and gains the control it was missing.

The two halves of the Rosters tab still did not match: theirs was a row of
fields and ours a row of text. They match now, and ours does the thing that
turned out to be missing entirely.

Once a game is live the lineup sheet is unreachable - the live tab shows the
scoring console instead - so there was no way to scratch a player who got
hurt or dress one who turned up late. The action column does it: scratch,
dress, and which goaltender is in net.

What stays read-only is the number, the name and the position. Those belong
to the season roster rather than to this game, so typing here would rename a
player in every game of the year to fix one night. They are rendered as
fields all the same, because the point of this change was that the two
sheets look alike.

The action column is widened in both, so the two grids stay identical rather
than identical-until-somebody-looks.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------------- the writes
sub("""  const bumpLine = (playerId, deltas) =>""",
    """  /* Dressed or scratched, for this game only. Written the way every live
     entry is - straight through and published - because the pickers read it
     the moment it changes. */
  const setDressed = (playerId, on) => {
    setDraft((st) => {
      const all = st.gameStats || {};
      const forGame = all[game.id] || {};
      const cur = forGame[playerId] || { g: 0, a: 0, pim: 0 };
      return { ...st, gameStats: { ...all, [game.id]: { ...forGame, [playerId]: { ...cur, dressed: on } } } };
    });
    /* A scratched goaltender cannot be the one in net. */
    if (!on && live.goalieUs === playerId) setLive({ goalieUs: "" });
    else publish();
  };

  const bumpLine = (playerId, deltas) =>""")

# --------------------------------------------------------------- the rows
sub("""                  {list.map((p) => (
                    /* Same row as theirs, read instead of typed - the lineup
                       sheet is what decides this, not this tab. */
                    <div className={"opprow oppsheetrow ausheetread"
                      + (title === "Scratched" ? " out" : "")} key={p.id}>
                      <span>{p.number || "\\u2014"}</span>
                      <span>{p.name}</span>
                      <span>{p.position === "D" || p.position === "G" ? p.position : p.spot || "F"}</span>
                      <span>{live.goalieUs === p.id ? "In net" : ""}</span>
                    </div>
                  ))}""",
    """                  {list.map((p) => {
                    const out = title === "Scratched";
                    const keeper = p.position === "G";
                    return (
                      /* Their row, with the two things that belong to this
                         game rather than to the season made live: who is
                         dressed, and who is in net. The rest is shown as
                         fields to match, and is not typed here - a number
                         changed on this tab would be changed for every game
                         of the season. */
                      <div className={"opprow oppsheetrow" + (out ? " ausheetout" : "")} key={p.id}>
                        <input value={p.number || ""} readOnly tabIndex={-1} placeholder="\\u2014" />
                        <input value={p.name || ""} readOnly tabIndex={-1} />
                        <input value={p.position === "D" || keeper ? p.position : p.spot || "F"}
                          readOnly tabIndex={-1} />
                        {keeper && !out ? (
                          <button className={"btn bSm " + (live.goalieUs === p.id ? "bLive" : "bGhost")}
                            title={live.goalieUs === p.id ? "In net" : "Put them in net"}
                            onClick={() => setLive({
                              goalieUs: p.id,
                              netBase: { shots: live.shotsThem || 0, goals: live.them || 0 },
                            })}>
                            In net
                          </button>
                        ) : (
                          <button className="btn bGhost bSm"
                            title={out ? "Dress them" : "Take them out of the lineup"}
                            onClick={() => setDressed(p.id, out)}>
                            {out ? "Dress" : "Scratch"}
                          </button>
                        )}
                      </div>
                    );
                  })}""")

# ------------------------------------------------------------------- CSS
sub(""".adminui .opprow.oppsheetrow { grid-template-columns: 52px 1fr 64px 30px; }""",
    """/* The last column carries a word on our sheet and a cross on theirs, and
   the two have to measure the same or the tab reads as two tables. */
.adminui .opprow.oppsheetrow { grid-template-columns: 52px 1fr 64px 84px; }""")

sub("""/* Our bench in the visitors' row: same grid, read instead of typed. The
   padding matches an input's so the two lists line up column for column
   down the tab. */
.adminui .ausheetread span { padding: 7px 9px; font-size: 13.5px; color: var(--au-text);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.adminui .ausheetread span:last-child { font-size: 11px; font-weight: 700;
  color: var(--au-warn, #F5B544); text-align: center; }
.adminui .ausheetread.out span { color: var(--au-faint); }""",
    """/* Read-only fields: the same box as an editable one, without the invitation
   to type in it. No focus ring, no caret, and the cursor says so. */
.adminui .oppsheetrow input[readonly] { cursor: default; color: var(--au-dim); }
.adminui .oppsheetrow input[readonly]:focus { outline: none; border-color: var(--au-line); }
/* Scratched: still legible, plainly not on the bench. */
.adminui .ausheetout input[readonly] { opacity: 0.55; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('our sheet is the same sheet')
