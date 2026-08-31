# -*- coding: utf-8 -*-
"""Show every game time in the reader's own timezone.

Times arrive from the league as a display string with the zone baked in -
"8:00 pm PDT", "8:45 am MST" - which is right for whoever wrote it and wrong
for a parent in Boston. The abbreviation is the one useful thing in there: it
fixes the offset, so the string plus the date is a real instant, and an
instant can be printed wherever the reader is.

Anything that cannot be read that way is printed exactly as stored. A time
with no zone is not converted, because converting it would mean guessing which
zone it was written in.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:110])
    s = s.replace(old, new)


sub("""function fmtDate(iso) {""",
    """/* Offsets from UTC, in minutes. An abbreviation names an offset outright -
   MST is -7 whether it is Phoenix in July or Denver in January - so no
   daylight-saving arithmetic is needed on top. */
const TZ_OFFSET = {
  PDT: -420, PST: -480, MDT: -360, MST: -420,
  CDT: -300, CST: -360, EDT: -240, EST: -300,
  AKDT: -480, AKST: -540, HST: -600, UTC: 0, GMT: 0,
};

/** A stored date and time as a real instant, or null when the zone is unknown. */
function gameInstant(iso, time) {
  if (!iso || !time) return null;
  const m = String(time).trim()
    .match(/^(\\d{1,2})(?::(\\d{2}))?\\s*([ap])\\.?m\\.?\\s+([A-Z]{2,4})$/i);
  if (!m) return null;
  const off = TZ_OFFSET[m[4].toUpperCase()];
  if (off === undefined) return null;
  let hour = Number(m[1]) % 12;
  if (/p/i.test(m[3])) hour += 12;
  const mins = Number(m[2] || 0);
  const [y, mo, d] = iso.split("-").map(Number);
  if (!y || !mo || !d) return null;
  /* Build the wall-clock moment as if it were UTC, then undo the zone's
     offset to get the true instant. */
  return new Date(Date.UTC(y, mo - 1, d, hour, mins) - off * 60000);
}

/**
 * A game's start, in whatever zone the reader is in.
 *
 * Falls back to the stored string when there is nothing to convert - a time
 * with no zone on it, or a zone this does not know - because printing it
 * unchanged is honest and guessing is not.
 */
function localTime(iso, time) {
  const at = gameInstant(iso, time);
  if (!at) return time || "";
  const parts = at.toLocaleTimeString("en-US", {
    hour: "numeric", minute: "2-digit", timeZoneName: "short",
  });
  return parts.replace(/\\bAM\\b/, "am").replace(/\\bPM\\b/, "pm");
}

/** The date a game falls on for the reader, which a late game can shift. */
function localDate(iso, time) {
  const at = gameInstant(iso, time);
  if (!at) return fmtDate(iso);
  return at.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
}

function fmtDate(iso) {""")

# ------------------------------------------------------- the public sites
pairs = [
    # scoreboard strip
    ("""                      : <>{fmtDate(g.date).replace(/^\\w+,?\\s*/, "")}, {r ? "Final" : g.time}</>}""",
     """                      : <>{localDate(g.date, g.time).replace(/^\\w+,?\\s*/, "")}, {r ? "Final" : localTime(g.date, g.time)}</>}"""),
    # game centre chip
    ("""                  <span className="gcchip">{game.time || "TBD"}</span>""",
     """                  <span className="gcchip">{localTime(game.date, game.time) || "TBD"}</span>"""),
    # game info rows (two of them, identical)
    ("""<dd>{fmtDate(game.date)}{game.time ? " \· " + game.time : ""}</dd>""",
     """<dd>{localDate(game.date, game.time)}{game.time ? " \· " + localTime(game.date, game.time) : ""}</dd>"""),
    # preview header
    ("""            {game.time && <p>{game.time}</p>}""",
     """            {game.time && <p>{localTime(game.date, game.time)}</p>}"""),
    # season series card foot
    ("""                    : st === "live" ? "Live" : (g.time || "TBD")}""",
     """                    : st === "live" ? "Live" : (localTime(g.date, g.time) || "TBD")}"""),
    # calendar cell
    ("""                      : <span className="caltime">{g.time || "TBD"}</span>}""",
     """                      : <span className="caltime">{localTime(g.date, g.time) || "TBD"}</span>}"""),
    # schedule table view
    ("""                        <td>{r ? <strong style={{ color: "var(--blue)" }}><span className={"rtag " + r.tag}>{r.tag}</span>, {g.result.us} - {g.result.them}{decidedIn(g.result)}</strong> : g.time}</td>""",
     """                        <td>{r ? <strong style={{ color: "var(--blue)" }}><span className={"rtag " + r.tag}>{r.tag}</span>, {g.result.us} - {g.result.them}{decidedIn(g.result)}</strong> : localTime(g.date, g.time)}</td>"""),
    # schedule row date line
    ("""                          <strong style={{ color: "var(--ink)" }}>{fmtDateParen(g.date)}</strong> \· <IcClock size={13} style={{ marginRight: 4 }} />{g.time}""",
     """                          <strong style={{ color: "var(--ink)" }}>{fmtDateParen(g.date)}</strong> \· <IcClock size={13} style={{ marginRight: 4 }} />{localTime(g.date, g.time)}"""),
    # quick look
    ("""                        <span><strong>Date:</strong> {fmtDate(g.date)} \· {g.time}</span>""",
     """                        <span><strong>Date:</strong> {localDate(g.date, g.time)} \· {localTime(g.date, g.time)}</span>"""),
    # schedule PDF
    ("""                      <td>{r ? `${r.tag}, ${g.result.us}-${g.result.them}${g.result.ot ? " (OT)" : ""}` : g.time}</td>""",
     """                      <td>{r ? `${r.tag}, ${g.result.us}-${g.result.them}${g.result.ot ? " (OT)" : ""}` : localTime(g.date, g.time)}</td>"""),
    # home banner
    ("""                  {featureState === "scheduled" && feature.time ? " \· " + feature.time : ""}""",
     """                  {featureState === "scheduled" && feature.time ? " \· " + localTime(feature.date, feature.time) : ""}"""),
]
for a, b in pairs:
    n = s.count(a)
    assert n >= 1, a[:90]
    s = s.replace(a, b)
    print('%d  %s' % (n, a.strip()[:60]))

io.open(p, 'w', encoding='utf-8').write(s)
print('timezone conversion wired')
