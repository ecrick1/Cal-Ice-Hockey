"""The Alumni sign-up: public page, stored submissions, admin inbox."""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:100])
    s = s.replace(old, new)


# ------------------------------------------------------------ app state
sub("""  const [recruits, setRecruits] = useState([]);""",
    """  const [recruits, setRecruits] = useState([]);
  const [alumni, setAlumni] = useState([]);""")

sub("""      const r = await loadKey(RECRUITS_KEY, []);""",
    """      const r = await loadKey(RECRUITS_KEY, []);
      const al = await loadKey(ALUMNI_KEY, []);""")

sub("""      setRecruits(r);""",
    """      setRecruits(r);
      setAlumni(al);""")

sub("""  useEffect(() => { if (loaded.current) saveKey(RECRUITS_KEY, recruits); }, [recruits]);""",
    """  useEffect(() => { if (loaded.current) saveKey(RECRUITS_KEY, recruits); }, [recruits]);
  useEffect(() => { if (loaded.current) saveKey(ALUMNI_KEY, alumni); }, [alumni]);""")

# ------------------------------------------------------------- routing
sub("""      {view === "venue" && <VenuePage site={pub} />}""",
    """      {view === "venue" && <VenuePage site={pub} />}
      {view === "alumni" && (
        <AlumniPage site={pub}
          onSubmit={(sub) => setAlumni((a) => [{ ...sub, id: uid(), submittedAt: new Date().toISOString() }, ...a])} />
      )}""")

sub("""        <Admin site={site} setSite={setSite} recruits={recruits} setRecruits={setRecruits}""",
    """        <Admin site={site} setSite={setSite} recruits={recruits} setRecruits={setRecruits}
          alumni={alumni} setAlumni={setAlumni}""")

# --------------------------------------------------------- the page
sub("""/**
 * The home rink, and how to get to it from campus.""",
    """const EMPTY_ALUMNI = {
  name: "", email: "", gradYear: "", years: "", number: "", position: "",
  city: "", note: "",
};

/**
 * The alumni list.
 *
 * A sign-up, not a directory: what somebody sends here goes to the program's
 * inbox and nowhere else. Nothing about a former player is published from it,
 * because nobody filling in a form has agreed to that.
 */
function AlumniPage({ site, onSubmit }) {
  const [form, setForm] = useState(EMPTY_ALUMNI);
  const [done, setDone] = useState(false);
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  const contact = (site.settings || {}).contactEmail;

  const submit = () => {
    if (!form.name.trim() || !form.email.trim()) return;
    onSubmit(form);
    setDone(true);
  };

  return (
    <main>
      <section className="phead">
        <div className="wrap">
          <p className="eyebrow">Alumni</p>
          <h1 className="h1" style={{ marginTop: 6 }}>Get on the list</h1>
          <p className="blg">
            Played for Cal? Leave your details and we will keep you posted on alumni
            games, reunions and how the program is going.
          </p>
        </div>
      </section>
      <section className="section">
        <div className="wrap" style={{ maxWidth: 820 }}>
          {done ? (
            <div className="card" role="status" style={{ textAlign: "center" }}>
              <p className="eyebrow" style={{ color: "var(--blue)" }}>You're on it</p>
              <h2 className="h2" style={{ color: "var(--blue)", margin: "8px 0 12px" }}>Welcome back.</h2>
              <p style={{ color: "var(--muted)", lineHeight: 1.6 }}>
                We will be in touch before the next alumni game.
              </p>
              <button className="btn bNavy bSm" style={{ marginTop: 18 }}
                onClick={() => { setForm(EMPTY_ALUMNI); setDone(false); }}>Add someone else</button>
            </div>
          ) : (
            <>
              <div className="fgrid">
                <div className="field"><label className="h6">Full name *</label>
                  <input value={form.name} onChange={set("name")} autoComplete="name" /></div>
                <div className="field"><label className="h6">Email *</label>
                  <input type="email" value={form.email} onChange={set("email")} autoComplete="email" /></div>
                <div className="field"><label className="h6">Years played</label>
                  <input value={form.years} onChange={set("years")} placeholder="2016–19" /></div>
                <div className="field"><label className="h6">Class year</label>
                  <input value={form.gradYear} onChange={set("gradYear")} placeholder="2019" /></div>
                <div className="field"><label className="h6">Jersey number</label>
                  <input value={form.number} onChange={set("number")} placeholder="26" /></div>
                <div className="field"><label className="h6">Position</label>
                  <select value={form.position} onChange={set("position")}>
                    <option value="">—</option>
                    {["Forward", "Defense", "Goaltender", "Staff"].map((x) => <option key={x}>{x}</option>)}
                  </select></div>
                <div className="field" style={{ gridColumn: "1 / -1" }}>
                  <label className="h6">Where you are now</label>
                  <input value={form.city} onChange={set("city")} placeholder="City, state" /></div>
                <div className="field" style={{ gridColumn: "1 / -1" }}>
                  <label className="h6">Anything you want us to know</label>
                  <textarea rows={4} value={form.note} onChange={set("note")} /></div>
              </div>
              <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap", marginTop: 20 }}>
                <button className="btn bGold" onClick={submit}
                  disabled={!form.name.trim() || !form.email.trim()}>
                  Add me to the list <IcArrowR size={16} />
                </button>
                <p className="bsm" style={{ margin: 0, color: "var(--muted)" }}>
                  Goes to the program, and nowhere else. Nothing here is published.
                </p>
              </div>
              {contact && (
                <p className="bsm" style={{ marginTop: 22, color: "var(--muted)" }}>
                  Rather just email? <a className="flegallink" href={"mailto:" + contact}>{contact}</a>
                </p>
              )}
            </>
          )}
        </div>
      </section>
    </main>
  );
}

/**
 * The home rink, and how to get to it from campus.""")

# ------------------------------------------------------------ admin nav
sub("""  ["Inbox", [["inbox", "Interest forms"]]],""",
    """  ["Inbox", [["inbox", "Interest forms"], ["alumni", "Alumni list"]]],""")

sub("""  inbox: "Recruit inbox",""",
    """  inbox: "Recruit inbox",
  alumni: "Alumni list",""")

sub("""function Admin({ site, setSite, recruits, setRecruits, authed, setAuthed, goto }) {""",
    """function Admin({ site, setSite, recruits, setRecruits, alumni, setAlumni, authed, setAuthed, goto }) {""")

sub("""            {k === "inbox" && unread > 0 && <span className="aubadge">{unread}</span>}""",
    """            {k === "inbox" && unread > 0 && <span className="aubadge">{unread}</span>}
                    {k === "alumni" && alumniUnread > 0 && <span className="aubadge">{alumniUnread}</span>}""")

sub("""            {tab === "inbox" && <Inbox recruits={recruits} setRecruits={setRecruits} />}""",
    """            {tab === "inbox" && <Inbox recruits={recruits} setRecruits={setRecruits} />}
            {tab === "alumni" && <AlumniInbox alumni={alumni} setAlumni={setAlumni} />}""")

# ------------------------------------------------------- admin inbox view
sub("""function Inbox({ recruits, setRecruits }) {""",
    """/* The alumni list. Same shape as the recruit inbox and deliberately plainer -
   there is no scouting to do here, only names to keep. */
function AlumniInbox({ alumni, setAlumni }) {
  const ask = useAsk();
  const [show, setShow] = useState("all");
  const unread = alumni.filter((a) => !a.read).length;
  const list = show === "unread" ? alumni.filter((a) => !a.read) : alumni;

  const remove = async (a) => {
    const ok = await ask({
      title: "Remove from the list?",
      message: (a.name || "This person") + " will be deleted from the alumni list.",
      detail: "This cannot be undone — there is no archive.",
      confirmLabel: "Delete",
      danger: true,
    });
    if (!ok) return;
    setAlumni((all) => all.filter((x) => x.id !== a.id));
  };

  const csv = () => {
    const rows = [["Name", "Email", "Years", "Class", "Number", "Position", "City", "Note", "Submitted"]];
    for (const a of alumni) {
      rows.push([a.name, a.email, a.years, a.gradYear, a.number, a.position, a.city,
        String(a.note || "").replace(/\\s+/g, " "), a.submittedAt]);
    }
    const text = rows.map((r) => r.map((c) => '"' + String(c || "").replace(/"/g, '""') + '"').join(",")).join("\\n");
    const url = URL.createObjectURL(new Blob([text], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url; a.download = "cal-hockey-alumni.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      {alumni.length > 0 && (
        <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap", marginBottom: 18 }}>
          <div className="tabs">
            {[["all", "All (" + alumni.length + ")"], ["unread", "New (" + unread + ")"]].map(([k, label]) => (
              <button key={k} className={"tab " + (show === k ? "on" : "")}
                onClick={() => setShow(k)}>{label}</button>
            ))}
          </div>
          <div style={{ marginLeft: "auto", display: "flex", gap: 9 }}>
            <button className="btn bGhost bSm" onClick={csv}>Export CSV</button>
            {unread > 0 && (
              <button className="btn bGhost bSm"
                onClick={() => setAlumni((all) => all.map((a) => ({ ...a, read: true })))}>
                Mark all read
              </button>
            )}
          </div>
        </div>
      )}

      {!alumni.length && (
        <div className="auempty">
          <p style={{ margin: 0, fontWeight: 600, color: "var(--au-text)" }}>Nobody on the list yet</p>
          <p className="bsm" style={{ margin: "6px 0 0" }}>
            Sign-ups from More → Alumni on the public site land here.
          </p>
        </div>
      )}
      {alumni.length > 0 && !list.length && (
        <div className="auempty"><p style={{ margin: 0 }}>Nothing new.</p></div>
      )}

      <div style={{ display: "grid", gap: 12 }}>
        {list.map((a) => (
          <article className="card" key={a.id}
            style={{ borderTopColor: a.read ? "var(--au-line)" : "var(--au-primary)" }}>
            <div style={{ display: "flex", gap: 12, alignItems: "baseline", flexWrap: "wrap" }}>
              {!a.read && <span className="savedot on" style={{ alignSelf: "center" }} aria-label="New" />}
              <h3 className="h3" style={{ color: "var(--au-text)" }}>{a.name}</h3>
              {a.years && <span className="pill pNext">{a.years}</span>}
              {a.position && <span className="bsm" style={{ color: "var(--au-dim)" }}>{a.position}</span>}
              {a.number && <span className="bsm" style={{ color: "var(--au-dim)" }}>#{a.number}</span>}
              <span className="bsm" style={{ marginLeft: "auto", color: "var(--au-dim)" }}>
                {a.submittedAt ? new Date(a.submittedAt).toLocaleDateString() : ""}
              </span>
            </div>
            <p className="bsm" style={{ margin: "8px 0 0" }}>
              <a className="flegallink" href={"mailto:" + a.email}>{a.email}</a>
              {a.city ? " · " + a.city : ""}
              {a.gradYear ? " · Class of " + a.gradYear : ""}
            </p>
            {a.note && <p className="bsm" style={{ margin: "10px 0 0", color: "var(--au-dim)", lineHeight: 1.6 }}>{a.note}</p>}
            <div style={{ display: "flex", gap: 9, marginTop: 14 }}>
              <button className="btn bGhost bSm"
                onClick={() => setAlumni((all) => all.map((x) => (x.id === a.id ? { ...x, read: !x.read } : x)))}>
                Mark {a.read ? "new" : "read"}
              </button>
              <button className="btn bGhost bSm" onClick={() => remove(a)}>Delete</button>
            </div>
          </article>
        ))}
      </div>
    </>
  );
}

function Inbox({ recruits, setRecruits }) {""")

io.open(p, 'w', encoding='utf-8').write(s)
print('alumni done')
