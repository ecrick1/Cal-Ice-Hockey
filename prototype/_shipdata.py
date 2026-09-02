# -*- coding: utf-8 -*-
"""A published copy ships with the site in it.

The prototype has always read the site out of the browser's own storage,
which is right on the machine it is being built on and useless anywhere
else: a visitor to a hosted copy has an empty storage, falls through to the
built-in seed, and gets a club with no seasons, no games and three news
items. Sixteen years of results existed only in one laptop.

So a build can carry a site.json beside it, and an empty storage reads that
before it reaches the seed. Fetched once, on the first load, and written to
storage the same as anything else - after which the visitor's own copy is
theirs to poke at without touching anybody else's.

The order matters and is the whole point: storage first, so a scorekeeper's
own work is never overwritten by the file the site shipped with; the file
second, so a stranger sees the real club; the seed last, so a build with no
file still runs.

A missing or malformed file is not an error worth stopping for - it means
this is a development copy, which is exactly what the seed is for.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


sub("""/* ---------------- Storage helpers ---------------- */
async function loadKey(key, fallback) {""",
    """/* ---------------- Storage helpers ---------------- */

/**
 * The site a published copy ships with.
 *
 * Storage is right on the machine the site is built on and empty everywhere
 * else, so a hosted copy would fall through to the seed and show a club with
 * no seasons. A build can carry site.json beside it; this is read only when
 * storage has nothing, and what it returns is then saved like any other edit.
 *
 * Missing or malformed means a development copy rather than a problem, and
 * the seed is exactly what that case is for.
 */
async function shippedSite() {
  try {
    const r = await fetch("./site.json", { cache: "no-store" });
    if (!r.ok) return null;
    const j = await r.json();
    return j && j.seasons ? j : null;
  } catch {
    return null;
  }
}

async function loadKey(key, fallback) {""")

sub("""      let s = await loadKey(SITE_KEY, SEED_SITE);""",
    """      /* Storage first, so nobody's own work is overwritten by the file the
         build shipped with. Then the shipped file, so a visitor sees the real
         club. Then the seed, so a copy with no file still runs. */
      let s = await loadKey(SITE_KEY, null);
      if (!s) s = (await shippedSite()) || SEED_SITE;""")

io.open(p, 'w', encoding='utf-8').write(s)
print('a build can ship its own site')
