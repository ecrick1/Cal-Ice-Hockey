# -*- coding: utf-8 -*-
"""A published change reaches somebody who has already been.

Shipping the site with the build fixed the first visit and broke every one
after it. Storage wins over the shipped file - which is right, because a
scorekeeper's own work must never be overwritten by the copy the build was
cut from - but it meant anybody who had loaded the site once held a frozen
copy for good. Publish a new build and returning visitors would see exactly
what they saw the first time, for ever, with no way to tell.

Every save already stamps a rev. So the build ships that number in a file of
its own, a few bytes rather than four megabytes, and a load compares it: the
same or older means the visitor has what was published, and newer means a
new build is up and worth fetching.

Which keeps the property that mattered. A scorekeeper's rev runs ahead of
whatever was last deployed, so their own work still wins; a visitor's is
whatever they were last given, so a new build reaches them. Somebody who
opens the console and edits their own copy runs ahead too and stops taking
updates, which is the right answer for a copy they have started changing.

The version file is fetched on every load and site.json only when it says to,
so the ordinary visit costs a few bytes and the ordinary reload costs
nothing.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


sub("""async function shippedSite() {
  try {
    const r = await fetch("./site.json", { cache: "no-store" });
    if (!r.ok) return null;
    const j = await r.json();
    return j && j.seasons ? j : null;
  } catch {
    return null;
  }
}""",
    """async function shippedSite() {
  try {
    const r = await fetch("./site.json", { cache: "no-store" });
    if (!r.ok) return null;
    const j = await r.json();
    return j && j.seasons ? j : null;
  } catch {
    return null;
  }
}

/**
 * The rev of the site this build shipped with, in a file of its own.
 *
 * A few bytes rather than four megabytes, because it is read on every load
 * and the thing it guards is only worth fetching when it has changed.
 * Missing means a development copy, which has nothing to publish.
 */
async function shippedRev() {
  try {
    const r = await fetch("./version.json", { cache: "no-store" });
    if (!r.ok) return null;
    const j = await r.json();
    return Number.isFinite(Number(j && j.rev)) ? Number(j.rev) : null;
  } catch {
    return null;
  }
}""")

sub("""      /* Storage first, so nobody's own work is overwritten by the file the
         build shipped with. Then the shipped file, so a visitor sees the real
         club. Then the seed, so a copy with no file still runs. */
      let s = await loadKey(SITE_KEY, null);
      if (!s) s = (await shippedSite()) || SEED_SITE;""",
    """      /* Storage first, so nobody's own work is overwritten by the file the
         build shipped with. Then the shipped file, so a visitor sees the real
         club. Then the seed, so a copy with no file still runs.

         And when a newer build has been published than the copy in storage,
         that copy is out of date rather than precious: every save stamps a
         rev, so a shipped rev above the stored one means an update is up. A
         scorekeeper's own rev runs ahead of whatever was last deployed, so
         their work still wins; a visitor's does not, so the update reaches
         them. */
      let s = await loadKey(SITE_KEY, null);
      let tookUpdate = false;
      if (!s) {
        s = (await shippedSite()) || SEED_SITE;
      } else {
        const up = await shippedRev();
        if (up != null && up > Number(s.rev || 0)) {
          const fresh = await shippedSite();
          if (fresh) { s = fresh; tookUpdate = true; }
        }
      }""")

# The fetched copy is written back, or every load pays for it again.
sub("""      setPendingState(pend);
      if (!Array.isArray(s.news)) s.news = SEED_SITE.news;""",
    """      setPendingState(pend);
      /* Written back, or the next load fetches the same four megabytes to
         reach the same conclusion. */
      if (tookUpdate) await saveKey(SITE_KEY, s);
      if (!Array.isArray(s.news)) s.news = SEED_SITE.news;""")

io.open(p, 'w', encoding='utf-8').write(s)
print('a published change reaches a returning visitor')
