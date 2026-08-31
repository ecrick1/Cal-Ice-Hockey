# -*- coding: utf-8 -*-
"""Rebuild the staff page as a directory rather than a contact list.

Three things were wrong with it.

The head coach's portrait was letterboxed. The photo column had no height of
its own, so the row was sized by the text beside it - and with no bio on file
that is three short lines, which squashed a square portrait into a 300x160
strip and left most of the block empty. The well has a portrait ratio now and
the text sits centred against it, so the block is the same shape whether
there is a bio or not.

The cards below were a circle with a name beside it and a stretch of white
after it: a list of contacts, not a staff page. They are portrait cards now -
photograph across the top, name and role under it - which is also the shape
the roster's card view already uses, so the two pages read as one site.

And four of the sixteen have no photograph. At 76px in a circle that was a
small grey silhouette; across the top of a card it would have been a large
one, four times over. Those get their initials instead.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------------------ markup
sub("""          {lead && (
            <article className="leadstaff">
              <div className="leadphoto">
                <PlayerAvatar size={260} flat photo={lead.photo} />
              </div>
              <div className="leadbody">
                <p className="eyebrow" style={{ color: "var(--blue)" }}>{lead.title}</p>
                <h2 className="leadname">{lead.name}</h2>
                {lead.since && <p className="leadsince">With the program since {lead.since}</p>}
                {lead.bio && <div className="leadbio">{renderArticle(lead.bio, () => {})}</div>}
                <div className="leadcontact">
                  {lead.email && <a className="fullbio" href={"mailto:" + lead.email}>{lead.email}</a>}
                  {lead.phone && <span className="bsm" style={{ color: "var(--muted)" }}>{lead.phone}</span>}
                </div>
              </div>
            </article>
          )}""",
    """          {lead && (
            <article className="leadstaff">
              <div className="leadphoto"><StaffFace person={lead} /></div>
              <div className="leadbody">
                <p className="eyebrow" style={{ color: "var(--blue)" }}>{lead.title}</p>
                <h2 className="leadname">{lead.name}</h2>
                {lead.since && <p className="leadsince">With the program since {lead.since}</p>}
                {lead.bio && <div className="leadbio">{renderArticle(lead.bio, () => {})}</div>}
                {(lead.email || lead.phone) && (
                  <dl className="leadcontact">
                    {lead.email && <><dt>Email</dt>
                      <dd><a href={"mailto:" + lead.email}>{lead.email}</a></dd></>}
                    {lead.phone && <><dt>Phone</dt>
                      <dd><a href={"tel:" + lead.phone.replace(/[^\\d+]/g, "")}>{lead.phone}</a></dd></>}
                  </dl>
                )}
              </div>
            </article>
          )}""")

sub("""              <div key={key} style={{ marginTop: 34 }}>
                <h2 className="statsec" style={{ marginBottom: 14 }}>{label}</h2>
                <div className="staffgrid">
                  {group.map((c) => (
                    <article className="staffcard" key={c.id}>
                      <PlayerAvatar size={76} photo={c.photo} />
                      <div style={{ minWidth: 0 }}>
                        <p className="staffname">{c.name}</p>
                        <p className="stafftitle">{c.title}</p>
                        {c.since && <p className="staffbio">Since {c.since}</p>}
                        {c.bio && <p className="staffbio">{c.bio}</p>}
                        {c.email && <a className="staffmail" href={"mailto:" + c.email}>{c.email}</a>}
                        {/* The editor takes a phone number, so the card has to show one -
                           otherwise it is typed in and silently goes nowhere. */}
                        {c.phone && <a className="staffmail" href={"tel:" + c.phone.replace(/[^\\d+]/g, "")}>{c.phone}</a>}
                      </div>
                    </article>
                  ))}
                </div>
              </div>""",
    """              <div className="staffsec" key={key}>
                <h2 className="staffseclab">{label}<span className="staffsecn">{group.length}</span></h2>
                <div className="staffgrid">
                  {group.map((c) => (
                    <article className="staffcard" key={c.id}>
                      <div className="staffwell"><StaffFace person={c} /></div>
                      <div className="staffbody">
                        <p className="staffname">{c.name}</p>
                        <p className="stafftitle">{c.title}</p>
                        {c.since && <p className="staffbio">Since {c.since}</p>}
                        {c.bio && <p className="staffbio">{c.bio}</p>}
                        {c.email && <a className="staffmail" href={"mailto:" + c.email}>{c.email}</a>}
                        {/* The editor takes a phone number, so the card has to show one -
                           otherwise it is typed in and silently goes nowhere. */}
                        {c.phone && <a className="staffmail" href={"tel:" + c.phone.replace(/[^\\d+]/g, "")}>{c.phone}</a>}
                      </div>
                    </article>
                  ))}
                </div>
              </div>""")

# ---------------------------------------------------------------- the face
sub("""function StaffPage({ site }) {""",
    """/**
 * A staff portrait, or their initials where there is no photograph on file.
 *
 * The generic silhouette is right at thumbnail size and wrong at this one -
 * a card-width grey figure says "missing" louder than the person's name says
 * anything. Initials fill the same well and read as a considered blank.
 */
function StaffFace({ person }) {
  if (person.photo) return <img className="stphoto" src={person.photo} alt="" aria-hidden="true" />;
  const initials = String(person.name || "")
    .trim().split(/\\s+/).slice(0, 2).map((w) => w[0] || "").join("").toUpperCase();
  return <span className="stmono" aria-hidden="true">{initials || "\\u2013"}</span>;
}

function StaffPage({ site }) {""")

# -------------------------------------------------------------------- CSS
sub(""".leadstaff { display: grid; grid-template-columns: 300px 1fr; gap: 0; background: #fff;
  border: 1px solid var(--border); border-radius: 14px; overflow: hidden; }
.leadphoto { background: var(--ice); }
.leadbody { padding: 30px 32px; }
.leadname { font-family: var(--body); font-weight: 800; font-size: clamp(1.6rem, 2.6vw, 2.2rem);
  letter-spacing: -0.02em; color: var(--ink); margin: 6px 0 4px; }
.leadsince { font-size: 13px; font-weight: 600; color: var(--muted); margin: 0 0 14px; }
.leadbio .artp { font-size: 15px; }
.leadcontact { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; margin-top: 14px; }""",
    """/* The photo column carries its own height. Sized by the text beside it, a
   head coach with no bio on file squashed a square portrait into a letterbox
   strip and left the rest of the block white. */
.leadstaff { display: grid; grid-template-columns: 320px minmax(0, 1fr); gap: 0; background: #fff;
  border: 1px solid var(--border); border-radius: 14px; overflow: hidden; }
.leadphoto { position: relative; background: var(--ice); min-height: 340px; }
.leadbody { padding: 30px 34px; align-self: center; }
.leadname { font-family: var(--body); font-weight: 800; font-size: clamp(1.6rem, 2.6vw, 2.2rem);
  letter-spacing: -0.02em; color: var(--ink); margin: 6px 0 4px; }
.leadsince { font-size: 13px; font-weight: 600; color: var(--muted); margin: 0 0 14px; }
.leadbio .artp { font-size: 15px; }
/* Labelled rows rather than a loose line of details: two facts with their
   names on them fill the space honestly where three words did not. */
.leadcontact { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 6px 18px;
  margin: 18px 0 0; padding-top: 16px; border-top: 1px solid var(--border); max-width: 420px; }
.leadcontact dt { font-size: 10.5px; font-weight: 800; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--muted); align-self: center; }
.leadcontact dd { margin: 0; font-size: 14px; font-weight: 650; }
.leadcontact a { color: var(--blue); text-decoration: none; }
.leadcontact a:hover { text-decoration: underline; text-decoration-thickness: 1px;
  text-underline-offset: 3px; text-decoration-color: var(--rule-on); }""")

sub("""/* Staff and prospect cards */
.staffgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.staffcard { display: flex; gap: 16px; align-items: flex-start; background: #fff;
  border: 1px solid var(--border); border-radius: 10px; padding: 18px; }
.staffcard svg, .staffcard img { border-radius: 8px; flex: 0 0 auto; }
.staffname { margin: 0; font-weight: 800; font-size: 17px; color: var(--ink); }
.stafftitle { margin: 4px 0 0; font-size: 13px; font-weight: 700; color: var(--blue); }
.staffbio { margin: 8px 0 0; font-size: 13px; line-height: 1.5; color: var(--muted); }""",
    """/* Staff cards: portrait over name, the same shape the roster's card view
   uses, so the two pages are recognisably the same site. */
.staffsec { margin-top: 36px; }
.staffseclab { font-family: var(--body); font-weight: 800; font-size: 13px; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--blue); margin: 0 0 14px; padding-bottom: 10px;
  border-bottom: 2px solid var(--gold); display: flex; align-items: center; gap: 10px; }
.staffsecn { font-family: var(--body); font-weight: 700; font-size: 11.5px; letter-spacing: 0;
  color: var(--muted); background: var(--ice); border-radius: 999px; padding: 2px 9px; }
.staffgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 18px; }
.staffcard { background: #fff; border: 1px solid var(--border); border-radius: 10px;
  overflow: hidden; }
.staffwell { position: relative; height: 230px; background: var(--ice); }
.stphoto { width: 100%; height: 100%; object-fit: cover; object-position: center top;
  display: block; background: var(--ice); }
.leadphoto .stphoto { position: absolute; inset: 0; }
/* Initials, where there is no photograph. Set large and faint: it fills the
   well without pretending to be a portrait. */
.stmono { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  font-family: var(--body); font-weight: 800; font-size: 46px; letter-spacing: 0.02em;
  color: var(--blue); opacity: 0.26; background: var(--ice); }
.staffbody { padding: 15px 16px 17px; }
.staffname { margin: 0; font-weight: 800; font-size: 16.5px; color: var(--ink); line-height: 1.25; }
.stafftitle { margin: 4px 0 0; font-size: 12.5px; font-weight: 700; color: var(--blue);
  line-height: 1.35; }
.staffbio { margin: 8px 0 0; font-size: 13px; line-height: 1.5; color: var(--muted); }""")

sub(""".staffmail { display: inline-block; margin-top: 8px; font-size: 13px; font-weight: 700;
  color: var(--blue); text-decoration: none; }""",
    """.staffmail { display: block; margin-top: 8px; font-size: 12.5px; font-weight: 700;
  color: var(--blue); text-decoration: none; overflow-wrap: anywhere; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('staff page rebuilt')
