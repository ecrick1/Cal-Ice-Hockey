# -*- coding: utf-8 -*-
"""Three changes:

  - A leader who has graduated is not one to watch. When the preview is
    describing last season, anybody listed as a senior or a grad that year is
    left out of the picks - they are not on the ice this time.
  - A setting to describe the current season instead, for a program that
    would rather show this year's numbers from the first game.
  - Fixture names on opponents removed altogether; a named game is set on the
    game.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:110])
    s = s.replace(old, new)


# ------------------------------------------------------------- the setting
sub("""    /* The university's own giving page, with the fund already selected. */
    donateUrl: "https://give.berkeley.edu/giftdetails?fund1=FU0852000",""",
    """    /* The university's own giving page, with the fund already selected. */
    donateUrl: "https://give.berkeley.edu/giftdetails?fund1=FU0852000",
    /* Which season a game preview describes before this one has been played:
       "previous" falls back to last year, "current" stays on this one and
       shows nothing until there are games. */
    previewForm: "previous",""")

sub("""/** The season a preview should describe: this one once it has games, else the last one that did. */
function formSeason(site, seasonName) {
  const own = site.seasons[seasonName];
  if ((own.schedule || []).some((g) => g.result)) return { name: seasonName, season: own, prior: false };""",
    """/** The season a preview should describe: this one once it has games, else the last one that did. */
function formSeason(site, seasonName) {
  const own = site.seasons[seasonName];
  if ((own.schedule || []).some((g) => g.result)) return { name: seasonName, season: own, prior: false };
  /* Some programs would rather show an empty this-year card than last year's
     names. Their call, not ours. */
  if (((site.settings || {}).previewForm) === "current") {
    return { name: seasonName, season: own, prior: false };
  }""")

# ------------------------------------------------- leave the leavers out
sub("""  const rows = (src.roster || []).map((p) => ({ p, t: boxScoreTotals(site, src, p) || p.stats || {} }));
  const skaters = rows.filter((x) => x.p.position !== "G");""",
    """  const rows = (src.roster || []).map((p) => ({ p, t: boxScoreTotals(site, src, p) || p.stats || {} }));

  /* Somebody who was a senior last year is not playing in this one, so they
     are no one to watch for. Only applied when the preview has fallen back to
     an earlier season - within a season everybody on the sheet is available -
     and only where a class is recorded, since a blank year is not a claim
     that somebody left. */
  const gone = (p) => form.prior && /^(sr|senior|gr|grad|graduate)$/i.test(String(p.year || "").trim());
  const available = rows.filter((x) => !gone(x.p));
  const skaters = available.filter((x) => x.p.position !== "G");""")

sub("""  const keepers = rows.filter((x) => x.p.position === "G" && (x.t.gp || 0) > 0)""",
    """  /* Same rule in net: a graduated keeper is not the one you will face. */
  const keepers = available.filter((x) => x.p.position === "G" && (x.t.gp || 0) > 0)""")

# A note, so a thin card is explained rather than looking broken.
sub("""        {!theirStats && (
          <p className="bsm gcnone gpnote">
            {live.loading
              ? "Reading their season from the league\\u2026"
              : "The league has no box scores for them this season. Paste their totals under Opponents and they appear here."}
          </p>
        )}""",
    """        {form.prior && rows.length !== available.length && (
          <p className="bsm gcnone gpnote">
            Last season's numbers, less the {rows.length - available.length} who
            graduated.
          </p>
        )}
        {!theirStats && (
          <p className="bsm gcnone gpnote">
            {live.loading
              ? "Reading their season from the league\\u2026"
              : "The league has no box scores for them this season. Paste their totals under Opponents and they appear here."}
          </p>
        )}""")

# --------------------------------------------------- fixture names, out
sub("""        /* What this fixture is known as. The opponent's standing name first,
           then anything this one game carries - a Senior Night against
           Stanford is both. */
        specials: [...new Set([(o && o.rivalry) || "", g.special || ""].filter(Boolean))],""",
    """        /* What this game is known as, if anything. */
        specials: g.special ? [g.special] : [],""")

sub("""      <div className="field" style={{ marginBottom: 20, maxWidth: 320 }}>
        <label className="h6">Fixture name</label>
        <input value={opponent.rivalry || ""} placeholder="The Big Freeze"
          onChange={(e) => setOpp(opponent.id, { rivalry: e.target.value })} />
        <p className="bsm" style={{ marginTop: 6, color: "var(--au-faint)" }}>
          Tags every game against them, past and future. A one-off like Senior Night
          goes on the game instead.
        </p>
      </div>

""", "")

sub("""        Open Roster on a team for their players, their season totals, and the name
        every game against them goes by.""",
    """        Open Roster on a team for their players and their season totals.""")

sub("""                  <p className="bsm" style={{ marginTop: 6, color: "var(--au-faint)" }}>
                    Shown as a gold tag on the schedule, the game page and the home
                    page. For a name that applies every year, set it on the opponent
                    instead — both show if a game has both.
                  </p>""",
    """                  <p className="bsm" style={{ marginTop: 6, color: "var(--au-faint)" }}>
                    Shown as a gold tag on the schedule, the game page and the home page.
                  </p>""")

io.open(p, 'w', encoding='utf-8').write(s)
print('done')
