# -*- coding: utf-8 -*-
"""Twenty-two dressed, and the last one is yours to spend.

The sheet allowed eighteen skaters and two goaltenders, both fixed, which
is twenty and not the rule. The rule is twenty-two on the sheet, and how
they are split is the coach's: nineteen and three if a third keeper is
worth carrying, twenty and two if the extra body is better used up front.

So there are three limits now rather than two, and they interact: no more
than twenty skaters, no more than three goaltenders, and no more than
twenty-two of them altogether. Nineteen and three fits; so does twenty and
two; twenty and three does not, and the sheet says which one is in the way
rather than refusing without explanation.

Fill dresses the goaltenders first and then takes skaters up to whatever is
left, because a sheet with no one in net is a worse starting point than one
a forward short.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ---------------------------------------------------------------- the caps
sub("""const MAX_SKATERS = 18;
const MAX_GOALIES = 2;""",
    """/* Twenty-two dress. The split is the coach's: nineteen skaters and three
   goaltenders, or twenty and two. Each part has its own ceiling as well, so
   twenty-two cannot be reached by dressing four keepers. */
const MAX_SKATERS = 20;
const MAX_GOALIES = 3;
const MAX_DRESSED = 22;

/* Which of the three limits a player would run into, or null if none does.
   Named rather than boolean because the sheet has to say which. */
function dressBlock(kind, skaters, goalies) {
  if (skaters + goalies >= MAX_DRESSED) return "dressed";
  if (kind === "G" && goalies >= MAX_GOALIES) return "goalies";
  if (kind !== "G" && skaters >= MAX_SKATERS) return "skaters";
  return null;
}

const BLOCK_TEXT = {
  dressed: MAX_DRESSED + " players are already dressed",
  goalies: MAX_GOALIES + " goaltenders are already dressed",
  skaters: MAX_SKATERS + " skaters are already dressed",
};""")

# ------------------------------------------------------------- the sheet
sub("""  const full = countSkaters(lu.dressed) >= MAX_SKATERS;
  const fullG = countGoalies(lu.dressed) >= MAX_GOALIES;""",
    """  const nSkaters = countSkaters(lu.dressed);
  const nGoalies = countGoalies(lu.dressed);
  const blockSkater = dressBlock("F", nSkaters, nGoalies);
  const blockGoalie = dressBlock("G", nSkaters, nGoalies);""")

sub("""      const p = roster.find((x) => x.id === id);
      if (p && p.position !== "G" && countSkaters(next) >= MAX_SKATERS) return;
      if (p && p.position === "G" && countGoalies(next) >= MAX_GOALIES) return;
      next.add(id);""",
    """      const p = roster.find((x) => x.id === id);
      if (p && dressBlock(p.position, countSkaters(next), countGoalies(next))) return;
      next.add(id);""")

sub("""  const Line = (props) => (
    <LineupRow {...props} lu={lu} full={full} fullG={fullG}
      max={MAX_SKATERS} maxG={MAX_GOALIES}
      onToggle={toggle} onStarter={toggleStarter} onNet={(id) => onWrite({ goalie: id })} />
  );""",
    """  const Line = (props) => (
    <LineupRow {...props} lu={lu} block={blockSkater} blockG={blockGoalie}
      onToggle={toggle} onStarter={toggleStarter} onNet={(id) => onWrite({ goalie: id })} />
  );""")

# ------------------------------------------------------------------- a row
sub("""function LineupRow({ p, starter, lu, full, fullG, max, maxG, onToggle, onStarter, onNet }) {
  const on = lu.dressed.has(p.id);
  const keeper = p.position === "G";
  const blocked = keeper ? !!fullG : !!full;
  const cap = keeper ? maxG : max;
  const capWord = keeper ? "goaltenders are" : "skaters are";
  return (
    <div className={"alurow" + (on ? "" : " out")}>
      <label className={"alupick" + (!on && blocked ? " blocked" : "")}
        title={!on && blocked ? cap + " " + capWord + " already dressed" : undefined}>""",
    """function LineupRow({ p, starter, lu, block, blockG, onToggle, onStarter, onNet }) {
  const on = lu.dressed.has(p.id);
  const keeper = p.position === "G";
  const blocked = keeper ? blockG : block;
  return (
    <div className={"alurow" + (on ? "" : " out")}>
      <label className={"alupick" + (!on && blocked ? " blocked" : "")}
        title={!on && blocked ? BLOCK_TEXT[blocked] : undefined}>""")

# ---------------------------------------------------------------- the state
sub("""  else if (skaters > MAX_SKATERS) {
    missing = "Only " + MAX_SKATERS + " skaters can dress — scratch "
      + (skaters - MAX_SKATERS) + " more, or use Fill to " + MAX_SKATERS + ".";
  } else if (goalies > MAX_GOALIES) {
    missing = "Only " + MAX_GOALIES + " goaltenders can dress — scratch "
      + (goalies - MAX_GOALIES) + " more.";
  } else if (goalies > 0 && !lu.goalie) missing = "Pick who starts in net.";
  return {
    skaters, goalies, missing,
    full: skaters >= MAX_SKATERS, fullG: goalies >= MAX_GOALIES,
  };""",
    """  else if (skaters > MAX_SKATERS) {
    missing = "Only " + MAX_SKATERS + " skaters can dress — scratch "
      + (skaters - MAX_SKATERS) + " more.";
  } else if (goalies > MAX_GOALIES) {
    missing = "Only " + MAX_GOALIES + " goaltenders can dress — scratch "
      + (goalies - MAX_GOALIES) + " more.";
  } else if (skaters + goalies > MAX_DRESSED) {
    missing = "Only " + MAX_DRESSED + " can dress — scratch "
      + (skaters + goalies - MAX_DRESSED) + " more. "
      + MAX_SKATERS + " and 2 in net, or " + (MAX_SKATERS - 1) + " and 3.";
  } else if (goalies > 0 && !lu.goalie) missing = "Pick who starts in net.";
  return {
    skaters, goalies, dressed: skaters + goalies, missing,
    full: !!dressBlock("F", skaters, goalies), fullG: !!dressBlock("G", skaters, goalies),
  };""")

# ------------------------------------------------------------------- fill
sub("""  const fillTo = (list, write, lu) => {
    const byNum = (a, b) => (Number(a.number) || 0) - (Number(b.number) || 0);
    const skatersFirst = list.filter((p) => p.position !== "G").sort(byNum).slice(0, MAX_SKATERS);
    const keepers = list.filter((p) => p.position === "G").sort(byNum).slice(0, MAX_GOALIES);
    const ids = [...skatersFirst, ...keepers].map((p) => p.id);""",
    """  /* Goaltenders first, then skaters into whatever is left of the twenty-two.
     A sheet with nobody in net is a worse place to start than one a forward
     short. */
  const fillTo = (list, write, lu) => {
    const byNum = (a, b) => (Number(a.number) || 0) - (Number(b.number) || 0);
    const keepers = list.filter((p) => p.position === "G").sort(byNum).slice(0, MAX_GOALIES);
    const room = Math.min(MAX_SKATERS, MAX_DRESSED - keepers.length);
    const skatersFirst = list.filter((p) => p.position !== "G").sort(byNum).slice(0, room);
    const ids = [...skatersFirst, ...keepers].map((p) => p.id);""")

sub("""                  const skatersFirst = was.filter((p) => p.position !== "G").sort(byNum).slice(0, MAX_SKATERS);
                  const keepers = was.filter((p) => p.position === "G").sort(byNum).slice(0, MAX_GOALIES);""",
    """                  const keepers = was.filter((p) => p.position === "G").sort(byNum).slice(0, MAX_GOALIES);
                  const room = Math.min(MAX_SKATERS, MAX_DRESSED - keepers.length);
                  const skatersFirst = was.filter((p) => p.position !== "G").sort(byNum).slice(0, room);""")

# ------------------------------------------------------------------ chips
sub("""      <span className={"aluchip" + (st.full ? " warn" : "")}>
        {st.skaters} of {MAX_SKATERS} skaters
      </span>
      <span className={"aluchip" + (st.fullG ? " warn" : "")}>
        {st.goalies} of {MAX_GOALIES} goaltenders
      </span>
      <span className="aluchip">{lu.starters.length} of 5 starting</span>""",
    """      <span className={"aluchip" + (st.dressed >= MAX_DRESSED ? " warn" : "")}>
        {st.dressed} of {MAX_DRESSED} dressed
      </span>
      <span className={"aluchip" + (st.full ? " warn" : "")}>{st.skaters} skaters</span>
      <span className={"aluchip" + (st.fullG ? " warn" : "")}>
        {st.goalies} goaltender{st.goalies === 1 ? "" : "s"}
      </span>
      <span className="aluchip">{lu.starters.length} of 5 starting</span>""")

sub("""              title={"Dresses the first " + MAX_SKATERS + " skaters by number, and every goaltender"}
              onClick={() => fillTo(roster, writeHome, home)}>Fill to {MAX_SKATERS}</button>""",
    """              title={"Dresses the goaltenders, then skaters by number up to " + MAX_DRESSED}
              onClick={() => fillTo(roster, writeHome, home)}>Fill to {MAX_DRESSED}</button>""")

sub("""                onClick={() => fillTo(theirs, writeAway, away)}>Fill to {MAX_SKATERS}</button>""",
    """                onClick={() => fillTo(theirs, writeAway, away)}>Fill to {MAX_DRESSED}</button>""")

io.open(p, 'w', encoding='utf-8').write(s)
print('dress caps rebuilt')
