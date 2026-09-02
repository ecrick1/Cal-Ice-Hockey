# -*- coding: utf-8 -*-
"""Wire the question up, and only record the answer that was actually given.

The dialog resolves the same value for Cancel, Escape and a click on the
backdrop, so "two people" cannot be told apart from "I hit Escape". Only the
affirmative writes anything: saying they are the same person joins the two
records, and anything else leaves them alone and inserts the mention as it
was going to anyway.

That means a genuinely different pair is asked about again next time, which
is a small cost against recording a decision somebody never made. The button
says what it does rather than "Cancel", which the dialog did not support and
now does.

The bulk Link players pass asks too - once per clashing name, before it
wraps anything - because it is the same decision made in a batch, and the
batch is where a wrong link would be least likely to be noticed.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# --------------------------------------------- the dialog can name its no
sub("""              <button className="btn bGhost bSm" onClick={() => onResolve(false)}>Cancel</button>""",
    """              {/* A question with two real answers needs the second one named.
                  Escape and the backdrop resolve this same value, so a caller
                  must not treat it as a deliberate "no". */}
              <button className="btn bGhost bSm" onClick={() => onResolve(false)}>
                {state.cancelLabel || "Cancel"}
              </button>""")

# ------------------------------------------------- only "same" is recorded
sub("""    const same = await ask({
      title: "Same person?",
      message: name + " is on this season's roster and also on the alumni list"
        + (played ? " (" + played + ")" : "") + ".",
      detail: "If they are the same person the mention links to their page and the "
        + "two records are joined. If they are two people who share a name, the "
        + "mention links to the player and the alumnus is left alone.",
      confirmLabel: "Same person",
      cancelLabel: "Two people",
    });
    /* Either answer is an answer, and both are recorded as identity: one id
       across both, or an id each. Having ids is what stops it asking again. */
    linkPerson(player, alum, same);
    return true;
  };""",
    """    const same = await ask({
      title: "Same person?",
      message: name + " is on this season's roster and also on the alumni list"
        + (played ? " (" + played + ")" : "") + ".",
      detail: "Same person joins the two records, and the mention links to their "
        + "page. Two people leaves both alone - the mention still links to the "
        + "player on this season's roster.",
      confirmLabel: "Same person",
      cancelLabel: "Two people",
    });
    /* Only the yes is recorded. Escape and the backdrop resolve the same
       value as the no, so treating a no as a decision would write one
       nobody made - and the cost of not recording it is being asked again. */
    if (same) linkPerson(player, alum);
    return true;
  };""")

# ------------------------------------------------------- joining the two
sub("""function NewsEditor({ site, setSite, alumni, setAlumni }) {""",
    """function NewsEditor({ site, setSite, alumni, setAlumni }) {
  /* One id across both records, adopting whichever already has one so that
     linking from two different stories does not mint two people. The roster
     row is written in every season it appears in, because a career is the
     seasons and not this one. */
  const linkPerson = (player, alum) => {
    const id = player.personId || alum.personId || uid();
    setSite((st) => ({
      ...st,
      seasons: Object.fromEntries(Object.entries(st.seasons || {}).map(([sn, se]) => [
        sn,
        {
          ...se,
          roster: (se.roster || []).map((x) => (personKey(x.name) === personKey(player.name)
            && !x.personId ? { ...x, personId: id } : x)),
        },
      ])),
    }));
    setAlumni((list) => (list || []).map((a) => (a.id === alum.id ? { ...a, personId: id } : a)));
  };
""")

# ---------------------------------------------------- pass it to the body
sub("""            <ArticleBody post={editing} setN={setN} players={players} />""",
    """            <ArticleBody post={editing} setN={setN} players={players}
              alumni={alumni} linkPerson={linkPerson} />""")

sub("""function ArticleBody({ post, setN, players, alumni, setAlumni, linkPerson }) {""",
    """function ArticleBody({ post, setN, players, alumni, linkPerson }) {""")

io.open(p, 'w', encoding='utf-8').write(s)
print('wired; only a real yes is recorded')
