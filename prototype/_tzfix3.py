# -*- coding: utf-8 -*-
"""Read the zone label by region and date, not by its letters.

The league's feed is careless with the D/S in an abbreviation: home games in
November and January come through as "7:30 pm PDT" and away games in January
as "8:30 pm MDT". Taken literally those are an hour out, and a strict reading
moved every winter home game an hour earlier than it is actually played.

So the letter that matters is the region - P, M, C, E - and whether the date
falls in daylight saving decides the rest. One exception, and it is a real
one: MST during the daylight-saving months is Arizona, which does not observe
it, so that offset is kept as written.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()

OLD_START = """/* Offsets from UTC, in minutes. An abbreviation names an offset outright -
   MST is -7 whether it is Phoenix in July or Denver in January - so no
   daylight-saving arithmetic is needed on top. */"""
OLD_END = """/** A stored date and time as a real instant, or null when the zone is unknown. */"""

i = s.index(OLD_START)
j = s.index(OLD_END)

NEW = """/* Standard-time offsets from UTC, in minutes, by region. Daylight saving is
   decided by the date rather than by the letter in the abbreviation, because
   the source is not careful about which one it writes. */
const TZ_REGION = { P: -480, M: -420, C: -360, E: -300, AK: -540, H: -600 };

/* Second Sunday in March to the first Sunday in November, US rules. Compared
   at day granularity, which is enough for a schedule - nothing faces off at
   two in the morning. */
function inUsDst(y, mo, d) {
  const nth = (month, n) => {
    const first = new Date(Date.UTC(y, month, 1)).getUTCDay();
    return 1 + ((7 - first) % 7) + (n - 1) * 7;
  };
  const start = nth(2, 2);
  const end = nth(10, 1);
  if (mo > 3 && mo < 11) return true;
  if (mo === 3) return d >= start;
  if (mo === 11) return d < end;
  return false;
}

"""

s = s[:i] + NEW + s[j:]

OLD_BODY = """  const off = TZ_OFFSET[m[4].toUpperCase()];
  if (off === undefined) return null;
  let hour = Number(m[1]) % 12;
  if (/p/i.test(m[3])) hour += 12;
  const mins = Number(m[2] || 0);
  const [y, mo, d] = iso.split("-").map(Number);
  if (!y || !mo || !d) return null;"""

NEW_BODY = """  const abbr = m[4].toUpperCase();
  const region = abbr.startsWith("AK") ? "AK" : abbr[0];
  const base = TZ_REGION[region];
  if (base === undefined) return null;
  let hour = Number(m[1]) % 12;
  if (/p/i.test(m[3])) hour += 12;
  const mins = Number(m[2] || 0);
  const [y, mo, d] = iso.split("-").map(Number);
  if (!y || !mo || !d) return null;
  /* Arizona writes MST all year and means it. Everywhere else, the date
     decides. */
  const arizona = abbr === "MST" && inUsDst(y, mo, d);
  const off = arizona ? base : base + (inUsDst(y, mo, d) ? 60 : 0);"""

assert s.count(OLD_BODY) == 1
s = s.replace(OLD_BODY, NEW_BODY)

io.open(p, 'w', encoding='utf-8').write(s)
print('zone reading rewritten')
