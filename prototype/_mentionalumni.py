# -*- coding: utf-8 -*-
"""Mentioning a name that is also on the alumni list asks who is meant.

A mention links a name in a story to a player's page. The picker offers this
season's roster, which is right - but a club has forty years of people and
some of the names come round again. Writing about Jack Burbank when there is
also a Jack Burbank on the alumni list is a question the console was not
asking and could not answer: it linked to the current player, silently, and
if the story was about the graduate it linked to the wrong man.

So it asks, once. Same person, or two people who share a name.

Either answer settles it, because both write an identity: the same id on
both records, or a separate id on each. Two records that both carry ids and
disagree are two people - which means the question is answered by having
been asked, and asking again would be nagging rather than checking.

It only asks where the ambiguity is real. A name on the roster and nowhere
else needs no question, and neither does one already answered.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------- alumni reach the editor
sub("""            {tab === "news" && <NewsEditor site={draft} setSite={setDraft} />}""",
    """            {tab === "news" && (
              <NewsEditor site={draft} setSite={setDraft}
                alumni={alumni} setAlumni={setAlumni} />
            )}""")

sub("""function NewsEditor({ site, setSite }) {""",
    """function NewsEditor({ site, setSite, alumni, setAlumni }) {""")

# ------------------------------------------------------- who shares a name
sub("""const MENTION_RE = /\\[\\[([^\\]]+)\\]\\]/g;""",
    """/* An alumnus with the same name as somebody on the roster.
 *
 * Only returns one where the question is still open. If both records carry a
 * personId the answer is already recorded - the same id means one person,
 * different ids mean two - and asking again would be nagging rather than
 * checking. */
function alumniClash(name, players, alumni) {
  const key = personKey(name);
  if (!key) return null;
  const player = (players || []).find((p) => personKey(p.name) === key);
  const alum = (alumni || []).find((a) => personKey(a.name) === key);
  if (!player || !alum) return null;
  if (player.personId && alum.personId) return null;
  return { player, alum };
}

const MENTION_RE = /\\[\\[([^\\]]+)\\]\\]/g;""")

# --------------------------------------------------------- and the asking
sub("""function ArticleBody({ post, setN, players }) {
  const ask = useAsk();
  const bodyRef = useRef(null);
  const [preview, setPreview] = useState(false);

  const linked = mentionedNames(post.body || "");

  const insertMention = (name) => {
    const el = bodyRef.current;
    const text = post.body || "";
    const token = "[[" + name + "]]";
    const at = el ? el.selectionStart : text.length;
    setN(post.id, { body: text.slice(0, at) + token + text.slice(el ? el.selectionEnd : at) });
  };""",
    """function ArticleBody({ post, setN, players, alumni, setAlumni, linkPerson }) {
  const ask = useAsk();
  const bodyRef = useRef(null);
  const [preview, setPreview] = useState(false);

  const linked = mentionedNames(post.body || "");

  /* A club has forty years of people and the names come round. Linking to
     this season's Jack Burbank when the story is about the one who graduated
     in 2014 is a wrong link, made silently, so it is asked about once. */
  const settleName = async (name) => {
    const clash = alumniClash(name, players, alumni);
    if (!clash) return true;
    const { player, alum } = clash;
    const played = [alum.years, alum.gradYear && "class of " + alum.gradYear]
      .filter(Boolean).join(", ");
    const same = await ask({
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
  };

  const insertMention = async (name) => {
    await settleName(name);
    const el = bodyRef.current;
    const text = post.body || "";
    const token = "[[" + name + "]]";
    const at = el ? el.selectionStart : text.length;
    setN(post.id, { body: text.slice(0, at) + token + text.slice(el ? el.selectionEnd : at) });
  };""")

io.open(p, 'w', encoding='utf-8').write(s)
print('the editor asks who is meant')
