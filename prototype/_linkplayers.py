# -*- coding: utf-8 -*-
"""A player is the same player as last year because somebody said so.

A career was assembled by matching names across seasons, exactly, character
for character. That works until it does not, and when it fails it fails
quietly in both directions: a player who starts going by Alex instead of
Alexander has two half-careers, a name typed with a different apostrophe has
two, and two different people who happen to share a name have one career
between them. Nothing on the page says which has happened.

So a roster row can carry a personId, and where one exists it decides. The
name is still the fallback, so nothing already entered changes until
somebody links it - this adds an answer rather than replacing the guess.

The linking is a review, not an import. The console finds the rows in
earlier seasons that look like the same person, says who and which years,
and links only what is confirmed. It never links on its own, because the
case it exists for - two people with one name - is exactly the case an
automatic pass would get wrong.

Matching for the suggestion is deliberately loose: case, punctuation and
accents ignored, so O'Dowd and ODowd are offered as the same man. Loose is
right for a suggestion and would be wrong for a decision, which is why a
person makes the decision.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ============================================== identity, and how it is read
sub("""/** Career totals for a name across every season. */
function careerTotals(site, name) {
  const t = { gp: 0, g: 0, a: 0, pim: 0, seasons: 0 };
  for (const season of Object.values(site.seasons || {})) {
    const p = (season.roster || []).find((x) => x.name === name);
    if (!p) continue;""",
    """/* One person across seasons.
 *
 * A personId is the answer somebody gave; a name is the guess made in its
 * absence. Both are here because the guess is right most of the time and
 * every roster already entered relies on it - linking adds certainty where
 * it matters rather than invalidating everything that came before.
 *
 * Two rows that both carry ids and disagree are two people, whatever their
 * names say. That is the whole point: a linked row is a decision, and a name
 * cannot overrule it. */
const nameKey = (n) => String(n || "")
  .normalize("NFD").replace(/[\\u0300-\\u036f]/g, "")
  .toLowerCase().replace(/[^a-z]/g, "");

function samePerson(a, b) {
  if (!a || !b) return false;
  if (a.personId && b.personId) return a.personId === b.personId;
  if (a.personId || b.personId) return false;
  return nameKey(a.name) === nameKey(b.name);
}

/* Every row across every season that is this person. */
function seasonsOf(site, player) {
  return Object.entries(site.seasons || {})
    .map(([sn, se]) => ({ sn, p: (se.roster || []).find((x) => samePerson(x, player)) }))
    .filter((r) => r.p);
}

/** Career totals for a player across every season. */
function careerTotals(site, name) {
  const t = { gp: 0, g: 0, a: 0, pim: 0, seasons: 0 };
  /* Called with a name from older call sites, and with a row from newer
     ones. A bare name has no id, which is exactly the fallback case. */
  const who = typeof name === "string" ? { name } : name;
  for (const season of Object.values(site.seasons || {})) {
    const p = (season.roster || []).find((x) => samePerson(x, who));
    if (!p) continue;""")

sub("""                  const across = Object.entries(site.seasons)
                    .map(([sn, se]) => ({ sn, p: (se.roster || []).find((x) => (x.name || "").trim() === (player.name || "").trim()) }))
                    .filter((r) => r.p);""",
    """                  const across = seasonsOf(site, player);""")

io.open(p, 'w', encoding='utf-8').write(s)
print('identity: an id when there is one, a name when there is not')
