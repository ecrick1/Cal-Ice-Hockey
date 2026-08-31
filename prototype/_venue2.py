"""Styles for the Venue page, and the Settings fields that drive it."""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:90])
    s = s.replace(old, new)


# ------------------------------------------------------------------- CSS
sub(
    """/* Power play / penalty kill tag */""",
    """/* Venue page */
.veneyebrow { font-family: var(--body); font-weight: 700; font-size: 12px;
  color: var(--muted); margin: 0 0 6px; }
.venfacts { display: flex; flex-wrap: wrap; gap: 10px 26px; margin: 18px 0 0; }
.venfact { display: inline-flex; align-items: center; gap: 9px; color: var(--ink);
  font-weight: 600; font-size: 14.5px; text-decoration: none; }
.venfact svg { color: var(--blue); flex: 0 0 auto; }
.venfact:hover { color: var(--blue); }
.venabout { margin-top: 22px; max-width: 68ch; }
.venabout p { color: var(--ink); line-height: 1.7; }
.venhead { font-family: var(--disp); font-weight: 700; font-size: 26px; letter-spacing: 0.01em;
  color: var(--ink); margin: 38px 0 4px; }
.vengrid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px; margin-top: 18px; }
.vencard { border: 1px solid var(--border); border-radius: 12px; background: #fff;
  padding: 18px 20px 6px; }
.venmode { display: flex; align-items: center; gap: 10px; }
/* The gold disc is the one bit of colour on the card, so the eye finds the
   three ways in before it reads any of them. */
.venicon { display: inline-flex; align-items: center; justify-content: center;
  width: 34px; height: 34px; border-radius: 999px; background: var(--gold);
  color: var(--deep); flex: 0 0 auto; }
.venmodename { margin: 0; font-size: 16px; font-weight: 800; color: var(--ink);
  letter-spacing: -0.01em; }
.venbody p { color: var(--muted); font-size: 14px; line-height: 1.65; }
.venmapbtn { margin-top: 26px; }
@media (max-width: 640px) {
  .venfacts { flex-direction: column; gap: 10px; }
  .venhead { font-size: 22px; margin-top: 30px; }
}

/* Power play / penalty kill tag */""")

# -------------------------------------------------------- admin settings
sub(
    """              <p className="bsm" style={{ marginTop: 6, color: "var(--au-faint)" }}>
                Prefilled on new home games. Away games take the opponent's rink and city.
              </p>
            </section>""",
    """              <p className="bsm" style={{ marginTop: 6, color: "var(--au-faint)" }}>
                Prefilled on new home games. Away games take the opponent's rink and city.
              </p>
            </section>

            <section className="card">
              <p className="h6" style={{ marginBottom: 4 }}>Venue page</p>
              <p className="bsm" style={{ marginBottom: 14 }}>
                What the public Venue tab shows. Clear a field and it stops appearing —
                better an absent line than a wrong one about somebody else's building.
              </p>
              {[
                ["name", "Rink name", "Oakland Ice Center"],
                ["address", "Address", "519 18th Street, Oakland, CA 94612"],
                ["phone", "Phone", "(510) 268-9000"],
                ["website", "Rink website", "https://www.oaklandice.com"],
                ["mapUrl", "Directions link", "https://www.google.com/maps/dir/?api=1&destination=…"],
              ].map(([k, label, ph]) => (
                <div className="field" key={k} style={{ marginTop: 12 }}>
                  <label className="h6">{label}</label>
                  <input value={(st.venue || {})[k] || ""} placeholder={ph}
                    onChange={setVenue(k)} />
                </div>
              ))}
              <div className="field" style={{ marginTop: 12 }}>
                <label className="h6">About the rink</label>
                <textarea rows={5} value={(st.venue || {}).about || ""}
                  placeholder="What the building is, who runs it, how many sheets."
                  onChange={setVenue("about")} />
              </div>

              <p className="h6" style={{ margin: "22px 0 4px" }}>Getting there</p>
              <p className="bsm" style={{ marginBottom: 10 }}>
                One card each on the public page. Empty ones are skipped.
              </p>
              {((st.venue || {}).directions || []).map((d, i) => (
                <div className="field" key={i} style={{ marginTop: 12 }}>
                  <label className="h6">{d.mode || "Untitled"}</label>
                  <textarea rows={4} value={d.body || ""}
                    onChange={setDirection(i)} />
                </div>
              ))}
            </section>""")

# The two setters the block above needs, beside the one already there.
sub(
    """  const setSetting = (k) => (e) =>""",
    """  /* Venue lives one level down in settings, and its directions one level
     below that, so each gets a setter rather than the call sites rebuilding
     the nesting by hand. */
  const setVenue = (k) => (e) => {
    const val = e && e.target ? e.target.value : e;
    setDraft((s) => ({
      ...s,
      settings: { ...(s.settings || {}),
        venue: { ...((s.settings || {}).venue || {}), [k]: val } },
    }));
  };
  const setDirection = (i) => (e) => {
    const val = e && e.target ? e.target.value : e;
    setDraft((s) => {
      const venue = (s.settings || {}).venue || {};
      const directions = [...(venue.directions || [])];
      directions[i] = { ...(directions[i] || {}), body: val };
      return { ...s, settings: { ...(s.settings || {}), venue: { ...venue, directions } } };
    });
  };

  const setSetting = (k) => (e) =>""")

io.open(p, 'w', encoding='utf-8').write(s)
print('css + admin done')
