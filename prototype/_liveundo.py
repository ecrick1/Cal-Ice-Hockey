# -*- coding: utf-8 -*-
"""Undo stops at the scoring console, and the Rosters tab shows both benches.

Three changes.

Undo belongs to the working copy: it walks back through edits nobody has
published yet. Live scoring does not work that way - every goal, penalty and
shot is written and published in the same breath, because a live score
behind a Save button is worse than no live score. So an undo there would
step the console back while the front page kept the goal. The buttons are
disabled while a game is being scored, with the reason on them, and they
come back the moment it ends.

They stay live for the lineup sheet, which is an ordinary draft edit - dress
a player, take them out again, undo. That is exactly what the user asked for
and it needs no exception, because the sheet does not publish.

"20 dressed for this game" was a footnote under the netminder picker on the
scoreboard, which is not where anyone looks for a roster. It moves to the
Rosters tab, where it is a heading for the list it describes.

And that tab showed their bench and not ours, which made it the opponent tab
wearing a plural name. Ours is there now: who dressed, who was scratched,
and who is in net.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ================================================= undo off during scoring
sub("""  const baseline = (pending && pending.site) || site;""",
    """  /* Live scoring publishes as it writes, so there is no unpublished step to
     walk back - undoing one would move the console and leave the front page
     where it was. The lineup sheet is an ordinary draft edit and keeps its
     undo; only the console itself is exempt. */
  const scoring = tab === "live" && Object.values(draft.seasons || {})
    .some((s2) => (s2.schedule || []).some((g) => g.live));

  const baseline = (pending && pending.site) || site;""")

sub("""              <span className="auundo">
                <button className="iconbtn" onClick={undo} disabled={!steps.undo}
                  title={steps.undo ? "Undo the last change" : "Nothing to undo"}
                  aria-label="Undo"><IcUndo /></button>
                <button className="iconbtn" onClick={redo} disabled={!steps.redo}
                  title={steps.redo ? "Redo" : "Nothing to redo"}
                  aria-label="Redo"><IcRedo /></button>
              </span>""",
    """              <span className="auundo">
                <button className="iconbtn" onClick={undo} disabled={scoring || !steps.undo}
                  title={scoring
                    ? "Not while a game is being scored — live entries publish as they are made"
                    : steps.undo ? "Undo the last change" : "Nothing to undo"}
                  aria-label="Undo"><IcUndo /></button>
                <button className="iconbtn" onClick={redo} disabled={scoring || !steps.redo}
                  title={scoring
                    ? "Not while a game is being scored"
                    : steps.redo ? "Redo" : "Nothing to redo"}
                  aria-label="Redo"><IcRedo /></button>
              </span>""")

# ============================================ the count moves off the bug
sub("""            <span className="bsm auopplink">
              {theirs.length
                ? theirs.length + (theirsFromSheet ? " dressed for this game" : " on their club roster")
                : "No roster for them yet"}
            </span>
""", "")

# ============================================== both benches on the tab
sub("""      {shownTab === "rosters" && (
        opponent && opponent.id
          ? <>""",
    """      {shownTab === "rosters" && (
        <>
          {/* Ours first: it is the list every picker on the scoring panel is
              offering, and the tab said "Rosters" while showing one bench. */}
          <section className="card" style={{ marginBottom: 18 }}>
            <div className="auopprosterhead">
              <p className="h6" style={{ margin: 0 }}>{usLabel} — this game</p>
              <span className="bsm" style={{ color: "var(--au-faint)" }}>
                {skaters.length} dressed
                {scratched.length ? " · " + scratched.length + " scratched" : ""}
              </span>
            </div>
            <div className="aulivesheet">
              {[["Forwards", skaters.filter((p) => p.position !== "G" && p.position !== "D")],
                ["Defense", skaters.filter((p) => p.position === "D")],
                ["Goaltenders", skaters.filter((p) => p.position === "G")]]
                .filter(([, list]) => list.length)
                .map(([title, list]) => (
                  <div className="alugroup" key={title}>
                    <div className="alugrouphead"><span>{title}</span><span>{list.length}</span></div>
                    {list.map((p) => (
                      <div className="alurow" key={p.id}>
                        <span className="alunum">#{p.number || "\\u2014"}</span>
                        <span className="aluname">{p.name}</span>
                        {live.goalieUs === p.id && <span className="alustart on">In net</span>}
                      </div>
                    ))}
                  </div>
                ))}
              {scratched.length > 0 && (
                <div className="alugroup">
                  <div className="alugrouphead"><span>Scratched</span><span>{scratched.length}</span></div>
                  {scratched.map((p) => (
                    <div className="alurow out" key={p.id}>
                      <span className="alunum">#{p.number || "\\u2014"}</span>
                      <span className="aluname">{p.name}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <p className="auhint" style={{ margin: "12px 0 0" }}>
              Set on the lineup sheet before the game. Anyone ejected comes off the
              pickers but stays here.
            </p>
          </section>

          {opponent && opponent.id
          ? <>""")

sub("""              <OpponentRoster opponent={opponent} setOpp={setOpp}
                achaSeasonId={(site.seasons[site.currentSeason] || {}).achaSeasonId}
                onClose={() => setTab("scoring")} />
            </>
          : <section className="card">
              <p className="h6" style={{ marginBottom: 6 }}>Rosters</p>
              <p className="auhint" style={{ margin: 0 }}>
                This game has no opponent from the library attached, so there is no
                roster to edit. Set one on the Schedule tab.
              </p>
            </section>""",
    """              <OpponentRoster opponent={opponent} setOpp={setOpp}
                achaSeasonId={(site.seasons[site.currentSeason] || {}).achaSeasonId}
                onClose={() => setTab("scoring")} />
            </>
          : <section className="card">
              <p className="h6" style={{ marginBottom: 6 }}>{oppName || "The other team"}</p>
              <p className="auhint" style={{ margin: 0 }}>
                This game has no opponent from the library attached, so there is no
                roster to edit. Set one on the Schedule tab.
              </p>
            </section>}
        </>""")

# Who did not dress, for the list above.
sub("""  const goalies = skaters.filter((p) => p.position === "G");""",
    """  const goalies = skaters.filter((p) => p.position === "G");
  /* Everyone on the roster who is not on the bench tonight - scratched
     before the game, or thrown out during it. */
  const scratched = [...roster]
    .filter((p) => !skaters.some((x) => x.id === p.id))
    .sort((a, b) => (Number(a.number) || 0) - (Number(b.number) || 0));""")

# ------------------------------------------------------------------- CSS
sub(""".adminui .aupenwait { border-left: 3px solid var(--au-warn, #F5B544); }""",
    """.adminui .aupenwait { border-left: 3px solid var(--au-warn, #F5B544); }
/* The bench, read rather than edited: the same rows as the lineup sheet
   without the checkboxes, because this tab reports what was decided there. */
.adminui .aulivesheet { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 14px; margin-top: 12px; }
.adminui .aulivesheet .alurow { padding: 5px 8px; }
.adminui .aulivesheet .aluname { font-size: 13px; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('undo gated, count moved, our bench shown')
