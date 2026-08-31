# -*- coding: utf-8 -*-
"""One way into a live game, and it goes through the lineup sheet.

The Live button on a schedule row went live on the spot: it wrote the live
session, put the game on the front page, and opened a scoring console inside
the Schedule tab. Nobody dressed anybody. The box score started empty, the
pickers had nobody in them, and the scratches were wrong on the game page
until someone went back and fixed them.

It now does what the Live scoring tab does, because it goes there: the tab
switches and the lineup sheet opens on that game - our sheet, then theirs,
then Start game or Open warm-up. That was already the only correct route in;
the schedule row was a second door that skipped the checklist.

The scoring console that used to live inside the Schedule tab goes with it.
Two consoles for one job is one too many, and only one of them dressed a
team first.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------- the console wiring
sub("""            {tab === "live" && (
              <LiveTab site={draft} setDraft={setDraft} updateSeason={updateSeason}
                onSave={save} dirty={dirty} />
            )}
            {tab === "schedule" && (
              <ScheduleEditor site={draft} setDraft={setDraft} updateSeason={updateSeason}
                onSave={save} dirty={dirty} />
            )}""",
    """            {tab === "live" && (
              <LiveTab site={draft} setDraft={setDraft} updateSeason={updateSeason}
                onSave={save} dirty={dirty}
                setupSeed={liveSeed} onSeedUsed={() => setLiveSeed(null)} />
            )}
            {tab === "schedule" && (
              <ScheduleEditor site={draft} setDraft={setDraft} updateSeason={updateSeason}
                onSave={save} dirty={dirty}
                openLive={(id) => { setLiveSeed(id); setTab("live"); }} />
            )}""")

# The seed lives on the console because the two tabs never exist at once.
sub("""  const [setupId, setSetupId] = useState(null);
  const setupGame = games.find((g) => g.id === setupId) || null;""",
    """  /* Seeded when the schedule sends a game here, so arriving on this tab
     opens that game's sheet rather than the list. Cleared on arrival - come
     back later and you get the list, the way you left it. */
  const [setupId, setSetupId] = useState(setupSeed || null);
  useEffect(() => { if (setupSeed) onSeedUsed && onSeedUsed(); }, []);
  const setupGame = games.find((g) => g.id === setupId) || null;""")

sub("""function LiveTab({ site, setDraft, updateSeason, onSave, dirty }) {""",
    """function LiveTab({ site, setDraft, updateSeason, onSave, dirty, setupSeed, onSeedUsed }) {""")

# ------------------------------------------------------- the schedule row
sub("""function ScheduleEditor({ site, setDraft, updateSeason: updateSeasonProp, onSave, dirty }) {""",
    """function ScheduleEditor({ site, setDraft, updateSeason: updateSeasonProp, onSave, dirty, openLive }) {""")

sub("""  const [openBox, setOpenBox] = useState(null);
  const [openMore, setOpenMore] = useState(null);
  const [liveId, setLiveId] = useState(null);""",
    """  const [openBox, setOpenBox] = useState(null);
  const [openMore, setOpenMore] = useState(null);""")

sub("""  const goLive = async (g) => {
    if (gameState(g) !== "live") {
      const today = new Date().toISOString().slice(0, 10);
      if (g.date && g.date !== today) {
        const when = new Date(g.date + "T12:00:00") < new Date(today + "T12:00:00") ? "was" : "is";
        const ok = await ask({
          title: "That game " + when + " not today",
          message: (oppName(g) || "This game") + " is scheduled for " + fmtDate(g.date) + ".",
          detail: "Going live puts it on the front page as happening right now. Check you picked the right row.",
          confirmLabel: "Go live anyway",
        });
        if (!ok) return;
      }
      setGame(g.id, {
        live: {
          period: "1", running: false,
          clockMs: periodSecs("1") * 1000, startedAt: null,
          us: 0, them: 0, intermission: false, penalties: [],
        },
      });
      onSave();
    }
    setLiveId(g.id);
  };""",
    """  /* Hands the game to Live scoring rather than starting one here. Nothing
     is written on the way: the lineup sheet is where a game goes live, and
     it is also where the box score gets its dressed players. */
  const goLive = (g) => { openLive && openLive(g.id); };""")

sub("""  const liveGame = games.find((g) => g.id === liveId);
  /* Fixed rather than content-sized: every row is its own grid, so a""",
    """  /* Fixed rather than content-sized: every row is its own grid, so a""")

sub("""  /* Its own screen, not a row that unfolds: this is used one-handed at the
     glass while the game is going on. */
  if (liveGame && gameState(liveGame) === "live") {
    return (
      <LiveGame game={liveGame} oppName={oppName(liveGame)}
        opponent={(site.opponents || []).find((o) => o.id === liveGame.opponentId)}
        roster={season.roster || []}
        site={site} setGame={setGame} setDraft={setDraft} publish={onSave} dirty={dirty}
        onClose={() => setLiveId(null)} />
    );
  }

  return (""",
    """  return (""")

# The row's own wording, now that the button is a way through rather than a
# switch that flips on the spot.
sub("""                title={
                  g.result ? "Game is already final"
                    : liveElsewhere && liveElsewhere.id !== g.id
                      ? "Another game is live — end it first"
                      : "Score this game as it happens"
                }""",
    """                title={
                  g.result ? "Game is already final"
                    : liveElsewhere && liveElsewhere.id !== g.id
                      ? "Another game is live — end it first"
                      : "Set the lineups and score this game in Live scoring"
                }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('live button routes through the lineup sheet')
