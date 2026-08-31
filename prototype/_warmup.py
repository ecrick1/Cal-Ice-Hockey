# -*- coding: utf-8 -*-
"""Warm-up, and one typeface in the home widget.

Going live had one door: Start game, which puts the clock on the front page
at 20:00 of the first period. But a stream goes up half an hour before the
puck drops, and the club wants the banner to say so. Warm-up is that state -
listed as live, clock parked, labelled for what it is - and it ends by
itself the first time the clock is started.

Separately: the two buttons on the home banner were set in different faces.
`.btn` never declares a family, so an anchor inherited the condensed display
face from the banner around it while a button fell back to the body face.
Same class, same size, two typefaces, decided by which element it happened
to be. They are declared now, in both places that pair them.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ----------------------------------------------------------------- the label
sub("""function liveLabel(live, now) {
  if (!live) return "";
  const p = live.period || "1";""",
    """function liveLabel(live, now) {
  if (!live) return "";
  /* Before the first faceoff. The game is listed - the stream is up, the
     doors are open - but there is no clock to report yet. */
  if (live.warmup) return "Warm-up";
  const p = live.period || "1";""")

# --------------------------------------------------------- going live warm
sub("""  const goLive = async (g, retro = false) => {""",
    """  const goLive = async (g, retro = false, warmup = false) => {""")

sub("""      live: {
        period: "1", running: false,
        clockMs: periodSecs("1") * 1000, startedAt: null,""",
    """      live: {
        period: "1", running: false, warmup: !!warmup,
        clockMs: periodSecs("1") * 1000, startedAt: null,""")

sub("""        setGame={setGame} onStart={() => goLive(setupGame)}
        onCancel={() => setSetupId(null)} />""",
    """        setGame={setGame} onStart={() => goLive(setupGame)}
        onWarmup={() => goLive(setupGame, false, true)}
        onCancel={() => setSetupId(null)} />""")

# ------------------------------------------------------- the lineup sheet
sub("""function LiveLineup({ game, roster, oppName, previous, opponent, setOpp, setGame, onStart, onCancel }) {""",
    """function LiveLineup({ game, roster, oppName, previous, opponent, setOpp, setGame, onStart, onWarmup, onCancel }) {""")

sub("""  const start = async () => {
    if (!theirs.length) {
      const ok = await ask({
        title: "No lineup for " + (oppName || "the other team"),
        message: "Their players will not appear in any picker, so every goal, assist and penalty against them has to be typed by hand.",
        detail: "Adding their sheet now also saves it for the next time you play them.",
        confirmLabel: "Start without it",
      });
      if (!ok) return;
    }
    onStart();
  };""",
    """  const start = async (warm) => {
    if (!theirs.length) {
      const ok = await ask({
        title: "No lineup for " + (oppName || "the other team"),
        message: "Their players will not appear in any picker, so every goal, assist and penalty against them has to be typed by hand.",
        detail: "Adding their sheet now also saves it for the next time you play them.",
        confirmLabel: "Start without it",
      });
      if (!ok) return;
    }
    if (warm) onWarmup(); else onStart();
  };""")

sub("""            <button className="btn bGhost" onClick={() => setStep(1)}>← Our lineup</button>
            <button className="btn bLive"
              disabled={theirs.length > 0 && !!awayState.missing}
              onClick={start}>
              Start game
            </button>""",
    """            <button className="btn bGhost" onClick={() => setStep(1)}>← Our lineup</button>
            {/* The stream goes up before the puck does. Warm-up lists the game
                on the front page with the clock parked; it ends by itself the
                first time the clock is started. */}
            <button className="btn bGhost"
              title="List the game as live with the clock parked at 20:00"
              disabled={theirs.length > 0 && !!awayState.missing}
              onClick={() => start(true)}>
              Open warm-up
            </button>
            <button className="btn bLive"
              disabled={theirs.length > 0 && !!awayState.missing}
              onClick={() => start(false)}>
              Start game
            </button>""")

# ------------------------------------------------- the clock ends warm-up
sub("""    const running = { running: true, clockMs: left, startedAt: Date.now() };""",
    """    /* Starting the clock is the end of the warm-up, whatever else it is. */
    const running = { running: true, clockMs: left, startedAt: Date.now(), warmup: false };""")

# ------------------------------------------------------------- the typeface
sub(""".hnextactions { margin-left: auto; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.hnextactions .btn { text-decoration: none; }""",
    """.hnextactions { margin-left: auto; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.hnextactions .btn { text-decoration: none; }
/* `.btn` sets no family of its own, so a link inherited the condensed face
   from the banner while a button fell back to the body one - the same pair
   of buttons in two typefaces, decided by which element each happened to be.
   Both bars declare it. */
.hnextactions .btn, .gpbar .btn { font-family: var(--body); }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('warm-up added, banner type settled')
