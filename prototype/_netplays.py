# -*- coding: utf-8 -*-
"""The net is on the sheet: changes, pulls, and whether a skater came on.

Who is in goal changed silently. A goaltender could be lifted after two soft
ones, or pulled with a minute left, and the play-by-play said nothing - so
reading a game back gave no idea when either happened, and a save percentage
built from it credited the wrong keeper for the rest of the period.

Every way the net changes now goes through one function and writes one play:
a change, a pull, or the goaltender coming back. And pulling asks the
question the sheet cannot work out for itself - whether a skater came on in
their place - because a net emptied for an extra attacker and a net emptied
for a delayed penalty look identical afterwards and mean different things.

One function rather than five call sites, because the play and the live
state have to be written together. Writing them separately is how the
delayed-penalty flag put a penalty back last week: the second write rebuilds
from the state the first one replaced.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------------ one way in
sub("""  const setLive = (patch) => push({ live: { ...live, ...patch } });""",
    """  const setLive = (patch) => push({ live: { ...live, ...patch } });

  /* The two sides say "empty" differently: ours holds a player id, theirs a
     typed name. */
  const NET_EMPTY = { us: "empty", them: "Empty net" };
  const netName = (side, v) => (!v || v === NET_EMPTY[side]
    ? "" : side === "us" ? nameOf(v) : String(v));

  /**
   * Every change of net, in one place: a substitution, a pull, or the
   * goaltender coming back.
   *
   * The play and the live state go in a single write. Two writes would have
   * the second rebuilt from the state the first replaced, which is how a
   * penalty came back from the dead once already.
   */
  const setNet = (side, value, extra) => {
    const us = side === "us";
    const key = us ? "goalieUs" : "goalieThem";
    const prev = live[key] || "";
    if (prev === value) return;
    const nowEmpty = value === NET_EMPTY[side];
    const wasEmpty = prev === NET_EMPTY[side];
    const patch = { [key]: value };
    patch[us ? "pulledUs" : "pulledThem"] = nowEmpty ? prev || "" : null;
    /* Shots faced are counted from the moment a keeper takes the net. */
    if (us) patch.netBase = { shots: live.shotsThem || 0, goals: live.them || 0 };
    const play = {
      id: uid(), kind: "goalie", team: side, ...whenNow(),
      phase: nowEmpty ? "pulled" : wasEmpty ? "back" : "change",
      player: netName(side, value),
      out: netName(side, prev),
      ...(nowEmpty ? { extra: !!extra } : {}),
    };
    push({ plays: [...plays, play], live: { ...live, ...patch } });
  };

  /* Pulling asks the one thing the sheet cannot work out: a net emptied for
     a sixth skater and a net emptied on a delayed penalty look the same
     afterwards and are not the same thing. */
  const [pullAsk, setPullAsk] = useState(null);""")

# --------------------------------------------------------- our net select
sub("""            <select value={live.goalieUs || ""}
              onChange={(e) => setLive({
                goalieUs: e.target.value,
                netBase: { shots: live.shotsThem || 0, goals: live.them || 0 },
              })}>""",
    """            <select value={live.goalieUs || ""}
              onChange={(e) => (e.target.value === "empty"
                ? setPullAsk({ side: "us" })
                : setNet("us", e.target.value))}>""")

sub("""              <button className={"btn bSm " + (live.goalieUs === "empty" ? "bLive" : "bGhost")}
                title="Goaltender off for an extra attacker"
                onClick={() => setLive(live.goalieUs === "empty"
                  ? { goalieUs: live.pulledUs || "", pulledUs: null }
                  : { goalieUs: "empty", pulledUs: live.goalieUs || "",
                      netBase: { shots: live.shotsThem || 0, goals: live.them || 0 } })}>
                {live.goalieUs === "empty" ? "Goalie back" : "Pull goalie"}
              </button>""",
    """              <button className={"btn bSm " + (live.goalieUs === "empty" ? "bLive" : "bGhost")}
                title="Goaltender off the ice"
                onClick={() => (live.goalieUs === "empty"
                  ? setNet("us", live.pulledUs || "")
                  : setPullAsk({ side: "us" }))}>
                {live.goalieUs === "empty" ? "Goalie back" : "Pull goalie"}
              </button>""")

# ------------------------------------------------------- their net select
sub("""              <select value={live.goalieThem || ""} onChange={(e) => setLive({ goalieThem: e.target.value })}>""",
    """              <select value={live.goalieThem || ""}
                onChange={(e) => (e.target.value === "Empty net"
                  ? setPullAsk({ side: "them" })
                  : setNet("them", e.target.value))}>""")

sub("""              <input value={live.goalieThem || ""} placeholder="Their goaltender"
                onChange={(e) => setLive({ goalieThem: e.target.value })} />""",
    """              <input defaultValue={live.goalieThem || ""} placeholder="Their goaltender"
                onBlur={(e) => setNet("them", e.currentTarget.value.trim())} />""")

sub("""              <button className={"btn bSm " + (live.goalieThem === "Empty net" ? "bLive" : "bGhost")}
                title="Their goaltender off for an extra attacker"
                onClick={() => setLive(live.goalieThem === "Empty net"
                  ? { goalieThem: live.pulledThem || "", pulledThem: null }
                  : { goalieThem: "Empty net", pulledThem: live.goalieThem || "" })}>
                {live.goalieThem === "Empty net" ? "Goalie back" : "Pull goalie"}
              </button>""",
    """              <button className={"btn bSm " + (live.goalieThem === "Empty net" ? "bLive" : "bGhost")}
                title="Their goaltender off the ice"
                onClick={() => (live.goalieThem === "Empty net"
                  ? setNet("them", live.pulledThem || "")
                  : setPullAsk({ side: "them" }))}>
                {live.goalieThem === "Empty net" ? "Goalie back" : "Pull goalie"}
              </button>""")

# ------------------------------------------------- the In net buttons
sub("""                          <button className={"btn bSm " + (live.goalieUs === p.id ? "bLive" : "bGhost")}
                            title={live.goalieUs === p.id ? "In net" : "Put them in net"}
                            onClick={() => setLive({
                              goalieUs: p.id,
                              netBase: { shots: live.shotsThem || 0, goals: live.them || 0 },
                            })}>
                            In net
                          </button>""",
    """                          <button className={"btn bSm " + (live.goalieUs === p.id ? "bLive" : "bGhost")}
                            title={live.goalieUs === p.id ? "In net" : "Put them in net"}
                            onClick={() => setNet("us", p.id)}>
                            In net
                          </button>""")

sub("""          <button className={"btn bSm " + (live && live.goalieThem === r.name ? "bLive" : "bGhost")}
            title={live && live.goalieThem === r.name ? "In net" : "Put them in net"}
            onClick={() => setLive && setLive({ goalieThem: r.name })}>
            In net
          </button>""",
    """          <button className={"btn bSm " + (live && live.goalieThem === r.name ? "bLive" : "bGhost")}
            title={live && live.goalieThem === r.name ? "In net" : "Put them in net"}
            onClick={() => setNet && setNet("them", r.name)}>
            In net
          </button>""")

sub("""function GameSheet({ game, oppName, site, setDraft, library, live, setLive }) {""",
    """function GameSheet({ game, oppName, site, setDraft, library, live, setNet }) {""")

sub("""          ? <GameSheet game={game} oppName={oppName} site={site} setDraft={setDraft}
              library={(opponent || {}).roster || []} live={live} setLive={setLive} />""",
    """          ? <GameSheet game={game} oppName={oppName} site={site} setDraft={setDraft}
              library={(opponent || {}).roster || []} live={live} setNet={setNet} />""")

# ------------------------------------------------------------------ the bar
sub("""      {saveAsk && (""",
    """      {pullAsk && (
        <div className="austop">
          <span className="h6">
            {(pullAsk.side === "us" ? usLabel : oppName || "Them")} — extra attacker on?
          </span>
          <span className="bsm">
            A net emptied for a sixth skater and one emptied on a delayed penalty
            read the same afterwards.
          </span>
          <button className="btn bGhost bSm" onClick={() => {
            setNet(pullAsk.side, NET_EMPTY[pullAsk.side], true); setPullAsk(null);
          }}>
            Yes — extra attacker
          </button>
          <button className="btn bGhost bSm" onClick={() => {
            setNet(pullAsk.side, NET_EMPTY[pullAsk.side], false); setPullAsk(null);
          }}>
            No
          </button>
          <button className="btn bGhost bSm austopskip" onClick={() => setPullAsk(null)}>
            Cancel
          </button>
        </div>
      )}

      {saveAsk && (""")

# ------------------------------------------------- reading it back later
sub("""                    ) : p.kind === "miss" ? (
                      <>
                        <span className="auplaykind stop">MISS</span>
                        <span className="auplaywho">{p.shooter || "Shot missed"}</span>
                      </>""",
    """                    ) : p.kind === "goalie" ? (
                      <>
                        <span className="auplaykind stop">NET</span>
                        <span className="auplaywho">
                          {p.phase === "pulled"
                            ? (p.out ? p.out + " pulled" : "Net empty")
                            : p.phase === "back"
                              ? (p.player ? p.player + " back in net" : "Goaltender back")
                              : (p.player || "Goaltender") + (p.out ? " in for " + p.out : " in net")}
                        </span>
                        {p.phase === "pulled" && (
                          <span className="auplayassist">
                            {p.extra ? "extra attacker" : "no extra attacker"}
                          </span>
                        )}
                      </>
                    ) : p.kind === "miss" ? (
                      <>
                        <span className="auplaykind stop">MISS</span>
                        <span className="auplaywho">{p.shooter || "Shot missed"}</span>
                      </>""", 2)

# ------------------------------------------------------ the public page
sub("""                    : x.kind === "miss" ? "Missed Shot\"""",
    """                    : x.kind === "goalie" ? (x.phase === "pulled" ? "Goaltender Pulled"
                      : x.phase === "back" ? "Goaltender Returns" : "Goaltender Change")
                    : x.kind === "miss" ? "Missed Shot\"""")

sub("""                    : x.kind === "miss"
                      ? (x.shooter ? withNumber(x.shooter, x.shooterId, mine) : abbr)
                        + " missed the net\"""",
    """                    : x.kind === "goalie"
                      ? (x.phase === "pulled"
                        ? abbr + (x.out ? " pull " + x.out : " empty the net")
                          + (x.extra ? " for an extra attacker" : "")
                        : x.phase === "back"
                          ? (x.player || abbr + " goaltender") + " back in net"
                          : (x.player || "A goaltender") + (x.out ? " in for " + x.out : " takes the net"))
                    : x.kind === "miss"
                      ? (x.shooter ? withNumber(x.shooter, x.shooterId, mine) : abbr)
                        + " missed the net\"""")

sub("""                  ["shot", "Shots on goal"], ["miss", "Missed shots"],""",
    """                  ["shot", "Shots on goal"], ["miss", "Missed shots"],
                  ["goalie", "Goaltending changes"],""")

sub("""                  const owned = x.kind === "penalty" || x.kind === "shot"
                    || x.kind === "timeout" || x.kind === "faceoff"
                    || x.kind === "miss" || x.kind === "shootout";""",
    """                  const owned = x.kind === "penalty" || x.kind === "shot"
                    || x.kind === "timeout" || x.kind === "faceoff"
                    || x.kind === "miss" || x.kind === "goalie" || x.kind === "shootout";""")

io.open(p, 'w', encoding='utf-8').write(s)
print('net changes are plays')
