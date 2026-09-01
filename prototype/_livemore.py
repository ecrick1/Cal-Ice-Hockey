# -*- coding: utf-8 -*-
"""Four things a scorekeeper needs and the console did not have.

  Any stoppage can be attributed after the fact. The prompt was removed
  because it slowed the whistle down; the correction is where that belongs,
  and until now the stoppage edit offered a reason and nothing else.

  A whistle for a penalty does not appear on the sheet until the penalty is
  entered. Logging both is logging the same event twice - "WHISTLE ·
  Penalty" a line above "PENALTY · 2 for tripping" says nothing the second
  line does not. So choosing that reason holds the time and waits, and the
  penalty carries it.

  A delayed penalty is a state the game is in, not an event. The arm goes
  up, play carries on, and the goaltender comes off. It shows on the bar,
  and it clears itself the moment the penalty it was waiting for arrives.

  And pulling the goaltender is one press. It was possible before - "Empty
  net" was in the netminder list - but a pulled goalie is a thing you do in
  the last minute with one hand, not a dropdown you go hunting in, and
  nothing said afterwards that the net was empty.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# =========================================================== the pending pen
sub("""  const ourKeeperId = live.goalieUs && live.goalieUs !== "empty" ? live.goalieUs : "";""",
    """  /* A whistle for a penalty, waiting for the penalty. Held rather than
     written: the penalty play carries this time when it arrives, and if it
     never does there was nothing to list. */
  const [penPending, setPenPending] = useState(null);
  const ourKeeperId = live.goalieUs && live.goalieUs !== "empty" ? live.goalieUs : "";""")

sub("""    setStopAsk(false);
    /* Only the freeze asks. Every other whistle is a reason and a time, and
       stopping to name someone for an icing costs the scorekeeper the next
       thing that happens. */
    if (reason === "Goalie freeze") setStopWho({ id: pid, reason });
  };""",
    """    setStopAsk(false);
    /* Only the freeze asks. Every other whistle is a reason and a time, and
       stopping to name someone for an icing costs the scorekeeper the next
       thing that happens. */
    if (reason === "Goalie freeze") setStopWho({ id: pid, reason });
  };

  /* Chosen "Penalty": nothing is written yet. The whistle and the penalty
     are one event, and the penalty entry is about to carry the time. */
  const holdForPenalty = () => {
    setStopAsk(false);
    setPenPending({ period: curPeriod, clock: fmtClock(left) });
  };""")

sub("""          {STOP_REASONS.map((r) => (
            <button className="btn bGhost bSm" key={r} onClick={() => logStop(r)}>{r}</button>
          ))}""",
    """          {STOP_REASONS.map((r) => (
            <button className="btn bGhost bSm" key={r}
              onClick={() => (r === "Penalty" ? holdForPenalty() : logStop(r))}>{r}</button>
          ))}""")

# The penalty takes the held time, and clears the hold and the delay with it.
sub("""    const at = elapsedSecs(live, now);
    const player = us ? nameOf(penPlayer) : theirName(penOpp);
    const playerId = us ? penPlayer : theirId(penOpp);
    const when = whenNow();""",
    """    const at = elapsedSecs(live, now);
    const player = us ? nameOf(penPlayer) : theirName(penOpp);
    const playerId = us ? penPlayer : theirId(penOpp);
    /* The whistle that stopped play for this is the time it happened at, not
       whenever the form was finished being filled in. */
    const when = penPending && !retro ? penPending : whenNow();""")

sub("""    setPenPlayer(""); setPenOpp("");
  };

  const endPenalty = (id) =>""",
    """    setPenPlayer(""); setPenOpp("");
    setPenPending(null);
    /* The arm comes down when the call is made. */
    if (live.delayed) setLive({ delayed: null });
  };

  const endPenalty = (id) =>""")

# A penalty shot is still a penalty: it clears the hold too.
sub("""      setPenPlayer(""); setPenOpp("");
      setPsAsk({ against: penTeam, infraction: penWhat, by: player });
      return;""",
    """      setPenPlayer(""); setPenOpp("");
      setPenPending(null);
      if (live.delayed) setLive({ delayed: null });
      setPsAsk({ against: penTeam, infraction: penWhat, by: player });
      return;""")

# Restarting play with nothing entered: the whistle produced no penalty, so
# there is nothing to list.
sub("""    setStopAsk(false);
    /* Play has restarted, so the question about the last whistle has gone
       with it - the stoppage keeps its reason and no name, the same as
       pressing skip. */
    setStopWho(null);""",
    """    setStopAsk(false);
    /* Play has restarted, so the question about the last whistle has gone
       with it - the stoppage keeps its reason and no name, the same as
       pressing skip. */
    setStopWho(null);
    /* And a penalty whistle nobody filled in was not a penalty. */
    setPenPending(null);""")

# ===================================================== the bar under the bug
sub("""      {/* ---- Strength ---- */}
      <div className={"austrength " + strength.kind.toLowerCase()}>""",
    """      {penPending && (
        <div className="austop aupenwait">
          <span className="h6">Whistle at {penPending.clock} — enter the penalty</span>
          <span className="bsm">It goes on the sheet with the penalty, not before it.</span>
          <button className="btn bGhost bSm austopskip" onClick={() => setPenPending(null)}>
            No penalty after all
          </button>
        </div>
      )}

      {/* ---- Strength ---- */}
      <div className={"austrength " + strength.kind.toLowerCase()}>""")

# ============================================ delayed penalty + empty net
sub("""              <button className="btn bSm bGhost" onClick={() => {
                if (live.running) setLive({ running: false, clockMs: left, startedAt: null });
                setStopAsk(false);
                setTimeoutAsk(true);
              }}>
                Timeout
              </button>""",
    """              <button className="btn bSm bGhost" onClick={() => {
                if (live.running) setLive({ running: false, clockMs: left, startedAt: null });
                setStopAsk(false);
                setTimeoutAsk(true);
              }}>
                Timeout
              </button>""")

sub("""          {!retro && (
            <div className="aubugnudge">""",
    """          {/* The arm is up and play has not stopped. A state the game is in
              rather than something that happened, so it is a toggle and not
              a play - and it clears itself when the penalty is called. */}
          {!retro && (
            <div className="audelayed">
              <span className="h6">Delayed penalty</span>
              {[["us", usLabel], ["them", oppName || "Them"]].map(([side, label]) => (
                <button key={side}
                  className={"btn bSm " + (live.delayed === side ? "bLive" : "bGhost")}
                  title={"Arm up against " + label}
                  onClick={() => setLive({ delayed: live.delayed === side ? null : side })}>
                  {label}
                </button>
              ))}
            </div>
          )}
          {!retro && (
            <div className="aubugnudge">""")

# The net, on both sides, as one press.
sub("""              <option value="">— nobody —</option>
              {goalies.map((p) => <option key={p.id} value={p.id}>#{p.number} {p.name}</option>)}
              <option value="empty">Empty net</option>
            </select>
          </div>""",
    """              <option value="">— nobody —</option>
              {goalies.map((p) => <option key={p.id} value={p.id}>#{p.number} {p.name}</option>)}
              <option value="empty">Empty net</option>
            </select>
            {!retro && (
              <button className={"btn bSm " + (live.goalieUs === "empty" ? "bLive" : "bGhost")}
                title="Goaltender off for an extra attacker"
                onClick={() => setLive(live.goalieUs === "empty"
                  ? { goalieUs: live.pulledUs || "", pulledUs: null }
                  : { goalieUs: "empty", pulledUs: live.goalieUs || "",
                      netBase: { shots: live.shotsThem || 0, goals: live.them || 0 } })}>
                {live.goalieUs === "empty" ? "Goalie back" : "Pull goalie"}
              </button>
            )}
          </div>""")

sub("""            ) : (
              <input value={live.goalieThem || ""} placeholder="Their goaltender"
                onChange={(e) => setLive({ goalieThem: e.target.value })} />
            )}""",
    """            ) : (
              <input value={live.goalieThem || ""} placeholder="Their goaltender"
                onChange={(e) => setLive({ goalieThem: e.target.value })} />
            )}
            {!retro && (
              <button className={"btn bSm " + (live.goalieThem === "Empty net" ? "bLive" : "bGhost")}
                title="Their goaltender off for an extra attacker"
                onClick={() => setLive(live.goalieThem === "Empty net"
                  ? { goalieThem: live.pulledThem || "", pulledThem: null }
                  : { goalieThem: "Empty net", pulledThem: live.goalieThem || "" })}>
                {live.goalieThem === "Empty net" ? "Goalie back" : "Pull goalie"}
              </button>
            )}""")

# What the bar says about all of it.
sub("""        <span className="austrengthtag">
          {strength.kind === "EV"
            ? "Even strength"
            : strength.kind + (strength.diff > 1 ? " +" + strength.diff : "")}
        </span>""",
    """        <span className="austrengthtag">
          {strength.kind === "EV"
            ? "Even strength"
            : strength.kind + (strength.diff > 1 ? " +" + strength.diff : "")}
        </span>
        {live.delayed && (
          <span className="audelaytag">
            Delayed penalty · {live.delayed === "us" ? usLabel : oppName || "Them"}
          </span>
        )}
        {live.goalieUs === "empty" && (
          <span className="auemptytag">{usLabel} net empty</span>
        )}
        {live.goalieThem === "Empty net" && (
          <span className="auemptytag">{oppName || "Them"} net empty</span>
        )}""")

# ======================================== attributing any stoppage, later
sub("""          {editPlay.kind === "stoppage" && (
            <select value={editDraft.reason || "Other"}
              onChange={(e) => setEditDraft({ ...editDraft, reason: e.target.value })}>
              {STOP_REASONS.map((r) => <option key={r}>{r}</option>)}
            </select>
          )}""",
    """          {editPlay.kind === "stoppage" && (
            <>
              <select value={editDraft.reason || "Other"}
                onChange={(e) => setEditDraft({ ...editDraft, reason: e.target.value })}>
                {STOP_REASONS.map((r) => <option key={r}>{r}</option>)}
              </select>
              {/* Whose it was, and who. Not asked at the whistle - that costs
                  the next thing that happens - but every stoppage can be
                  attributed here afterwards. */}
              <select value={editDraft.byTeam || ""}
                onChange={(e) => setEditDraft({
                  ...editDraft, byTeam: e.target.value || null, by: "", byId: null,
                })}>
                <option value="">— neither bench —</option>
                <option value="us">{usLabel}</option>
                <option value="them">{oppName || "Them"}</option>
              </select>
              {editDraft.byTeam === "us" && (
                <select value={editDraft.byId || ""}
                  onChange={(e) => setEditDraft({
                    ...editDraft,
                    byId: e.target.value || null,
                    by: e.target.value ? nameOf(e.target.value) : "",
                  })}>
                  <option value="">{usLabel} — no player</option>
                  {skaters.map((p) => (
                    <option key={p.id} value={p.id}>#{p.number} {p.name}</option>
                  ))}
                </select>
              )}
              {editDraft.byTeam === "them" && (theirs.length ? (
                <select value={editDraft.by || ""}
                  onChange={(e) => setEditDraft({ ...editDraft, by: e.target.value, byId: null })}>
                  <option value="">{oppName || "Them"} — no player</option>
                  {theirs.map((p) => (
                    <option key={p.id} value={p.name}>#{p.number} {p.name}</option>
                  ))}
                </select>
              ) : (
                <input className="auentryname" value={editDraft.by || ""}
                  placeholder={(oppName || "Their") + " player"}
                  onChange={(e) => setEditDraft({ ...editDraft, by: e.target.value, byId: null })} />
              ))}
            </>
          )}""")

# ------------------------------------------------------------------- CSS
sub(""".adminui .auentryname { width: 170px; flex: 0 0 auto; }""",
    """.adminui .auentryname { width: 170px; flex: 0 0 auto; }
/* Waiting on a penalty: the whistle has gone and the sheet is deliberately
   still empty, so the bar says so rather than leaving a gap. */
.adminui .aupenwait { border-left: 3px solid var(--au-warn, #F5B544); }
.adminui .audelayed { display: flex; align-items: center; gap: 6px; margin-top: 8px;
  justify-content: center; flex-wrap: wrap; }
.adminui .audelayed .h6 { margin: 0; }
.adminui .audelaytag, .adminui .auemptytag { font-size: 11.5px; font-weight: 700;
  border-radius: 999px; padding: 2px 10px; white-space: nowrap; }
.adminui .audelaytag { background: rgba(245,181,68,0.16); color: var(--au-warn, #F5B544); }
.adminui .auemptytag { background: rgba(127,127,127,0.16); color: var(--au-dim); }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('pending penalty, delayed penalty, empty net, stoppage attribution')
