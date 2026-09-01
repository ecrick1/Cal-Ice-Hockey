# -*- coding: utf-8 -*-
"""Skaters on the ice, not just who is up a man.

A penalty each was reported as even strength, because the model only ever
asked who had the advantage and the answer was nobody. But 4-on-4 is not
5-on-5: it is the most open ice in the game, and the one strength state a
viewer most wants named. Nothing anywhere said it.

So the model counts skaters per side rather than a differential, and the
rulebook decides the count:

  - Coincidental minors do not substitute (NHL 19.2). One each from 5-on-5
    is 4-on-4; two each is 3-on-3.
  - Coincidental majors do substitute (NHL 20.4). A fight leaves the teams
    at full strength, which is why a five and five cannot be treated the
    same way as a two and two.
  - No team ever has fewer than three skaters (NHL 19.1). A third penalty
    sends the player to the box without taking a fourth man off; its clock
    starts when an earlier one expires.

Which penalties are coincidental needs no new field and no new button. They
are the ones handed out at the same stoppage, and the clock is stopped while
they are entered, so they already share a start second to the exact tick.
That also means it works on the seasons already typed up, and on the 2-and-1
case the user asked about: the pair cancels, the extra one is a power play,
and both benches are still a man light - 4-on-3.

The whistle bar now stays up after the first penalty instead of closing, so
a second call at the same whistle is entered where the first one was rather
than being chased with the clock already stopped.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ===================================================== the model
sub("""/* Who is up a skater, if anyone. Coincidental penalties cancel, which is the
 * common case this has to get right; 5-on-3 shows as a two-player advantage
 * rather than being modelled as its own state.
 *
 * Only the penalties that actually take a skater off count. A misconduct is
 * ten minutes in the box with a substitute on the ice, so a team serving one
 * is at even strength and the console has to say so. Every running penalty
 * is still returned for the strip, because the box is worth seeing whether
 * or not it changes the count. */
function strengthState(live, now) {
  const active = activePenalties(live, now);
  const onIce = active.filter((p) => p.shorts);
  const us = onIce.filter((p) => p.team === "us").length;
  const them = onIce.filter((p) => p.team === "them").length;
  if (us === them) return { kind: "EV", diff: 0, active };
  return us > them
    ? { kind: "PK", diff: us - them, active }
    : { kind: "PP", diff: them - us, active };
}""",
    """/* Penalties handed out at the same stoppage are coincidental. Nothing has
   to record that: the clock is stopped while they are entered, so they were
   all stamped with the same elapsed second, to the tick. Reading it back out
   of the end time means it holds for games typed up long afterwards too. */
const penaltyStart = (p) => p.endsAt - (Number(p.minutes) || 0) * 60;

/* Majors substitute and minors do not, so the two never cancel against each
   other. Everything that sits a player down for five is grouped with the
   majors; a match penalty is served the same way. */
const penaltyClass = (p) => {
  const k = kindOf(p);
  return k === "major" || k === "match" ? "major" : "minor";
};

/**
 * How many skaters each side has on the ice.
 *
 * Counting skaters rather than the differential is what makes 4-on-4 sayable
 * at all: a penalty each is not even strength, and reporting it as such threw
 * away the most open ice in the game. The rulebook decides the count.
 *
 * Coincidental minors do not substitute (NHL 19.2) - one each from 5-on-5 is
 * 4-on-4, two each is 3-on-3 - while coincidental majors do (NHL 20.4), so a
 * fight leaves both benches full and cancels out of this entirely. Unequal
 * calls at one whistle sort themselves out: the pair cancels for advantage
 * and both sides still lose the man, which is how two against one comes to
 * be 4-on-3 rather than 5-on-4.
 *
 * No side ever goes below three (NHL 19.1). A third penalty is served without
 * a fourth skater coming off; its clock waits for an earlier one to expire.
 *
 * Only penalties that actually take a skater off are counted. A misconduct is
 * ten minutes in the box with a substitute on the ice, so a team serving one
 * is at full strength and the console has to say so. Every running penalty is
 * still returned for the strip, because the box is worth seeing whether or
 * not it changes the count.
 */
function strengthState(live, now) {
  const active = activePenalties(live, now);
  const serving = active.filter((p) => p.shorts);

  /* Coincidental majors put nobody in the box as far as the ice is
     concerned, so they come out before anything is counted. */
  const groups = {};
  for (const p of serving) {
    const key = penaltyStart(p) + "|" + penaltyClass(p);
    const g = groups[key]
      || (groups[key] = { major: penaltyClass(p) === "major", us: [], them: [] });
    (p.team === "us" ? g.us : g.them).push(p);
  }
  const substituted = new Set();
  for (const g of Object.values(groups)) {
    if (!g.major) continue;
    for (let i = 0; i < Math.min(g.us.length, g.them.length); i++) {
      substituted.add(g.us[i].id); substituted.add(g.them[i].id);
    }
  }

  const box = (team) => serving.filter((p) => p.team === team && !substituted.has(p.id)).length;
  const us = Math.max(3, 5 - box("us"));
  const them = Math.max(3, 5 - box("them"));
  const label = us === them ? us + "-on-" + us
    : Math.max(us, them) + "-on-" + Math.min(us, them);

  if (us === them) {
    /* Even, but not necessarily five a side. Four-on-four is its own state
       and gets its own name; only a full sheet is nothing worth saying. */
    return { kind: us === 5 ? "EV" : "E4", diff: 0, us, them, label, active };
  }
  return us > them
    ? { kind: "PK", diff: them - us, us, them, label, active }
    : { kind: "PP", diff: us - them, us, them, label, active };
}""")

# `diff` was a magnitude and is signed now; its one reader wanted the size.
sub("""        {st.diff > 1 ? " +" + st.diff : ""}""",
    """        {Math.abs(st.diff) > 1 ? " +" + Math.abs(st.diff) : ""}""")

# ===================================================== the public tag
sub("""function StrengthTag({ live, now, usAbbr, size }) {
  if (!live) return null;
  const st = strengthState(live, now);
  if (st.kind === "EV") return null;
  const pp = st.kind === "PP";""",
    """function StrengthTag({ live, now, usAbbr, size }) {
  if (!live) return null;
  const st = strengthState(live, now);
  if (st.kind === "EV") return null;

  /* Nobody is on a power play and it is still worth saying, because the ice
     is not what it was. Neither colour fits, so it gets its own. */
  if (st.kind === "E4") {
    const box = st.active.filter((x) => x.shorts).map((x) => x.left);
    return (
      <span className={"strtag ev4" + (size === "sm" ? " sm" : "")}>
        <span className="strtaglab">{st.label}</span>
        {box.length ? <span className="strtagclock">{fmtClock(Math.min(...box) * 1000)}</span> : null}
      </span>
    );
  }

  const pp = st.kind === "PP";""")

sub("""          : (usAbbr ? usAbbr + " " : "") + (pp ? "Power play" : "Penalty kill")}
        {Math.abs(st.diff) > 1 ? " +" + Math.abs(st.diff) : ""}""",
    """          : (usAbbr ? usAbbr + " " : "") + (pp ? "Power play" : "Penalty kill")}
        {" " + st.label}""")

# ===================================================== the console band
sub("""          {strength.kind === "EV"
            ? "Even strength"
            : strength.kind + (strength.diff > 1 ? " +" + strength.diff : "")}""",
    """          {strength.kind === "EV" ? "Even strength"
            : strength.kind === "E4" ? strength.label
            : strength.kind + " " + strength.label}""")

sub(""".adminui .austrength.pk { border-color: rgba(245,181,68,0.4); }
.adminui .austrength.pk .austrengthtag { color: var(--au-warn, #F5B544); }""",
    """.adminui .austrength.pk { border-color: rgba(245,181,68,0.4); }
.adminui .austrength.pk .austrengthtag { color: var(--au-warn, #F5B544); }
/* Even and short. Not a power play either way, so not either colour. */
.adminui .austrength.e4 { border-color: rgba(129,140,248,0.45); }
.adminui .austrength.e4 .austrengthtag { color: #A5B4FC; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('strength counts skaters')
