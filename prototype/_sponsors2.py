"""The Sponsors screen in the console."""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:100])
    s = s.replace(old, new)


sub("""  ["Library", [["opponents", "Opponents"], ["news", "News"]]],""",
    """  ["Library", [["opponents", "Opponents"], ["news", "News"], ["sponsors", "Sponsors"]]],""")

sub("""  news: "News",""",
    """  news: "News",
  sponsors: "Sponsors",""")

sub("""            {tab === "inbox" && <Inbox recruits={recruits} setRecruits={setRecruits} />}""",
    """            {tab === "sponsors" && <SponsorsEditor site={draft} setDraft={setDraft} />}
            {tab === "inbox" && <Inbox recruits={recruits} setRecruits={setRecruits} />}""")

sub("""/* The alumni list. Same shape as the recruit inbox and deliberately plainer -""",
    """/**
 * Sponsors, as they appear in the footer band above the copyright line.
 *
 * A logo is optional: with none, the footer prints the name instead, which is
 * better than a gap where a local rink or restaurant should be.
 */
function SponsorsEditor({ site, setDraft }) {
  const ask = useAsk();
  const list = site.sponsors || [];

  const setSponsors = (fn) =>
    setDraft((s) => ({ ...s, sponsors: fn(s.sponsors || []) }));
  const setOne = (id, patch) =>
    setSponsors((all) => all.map((x) => (x.id === id ? { ...x, ...patch } : x)));

  const add = () =>
    setSponsors((all) => [...all, { id: uid(), name: "", url: "", logo: "" }]);

  const move = (id, dir) =>
    setSponsors((all) => {
      const i = all.findIndex((x) => x.id === id);
      const j = i + dir;
      if (i < 0 || j < 0 || j >= all.length) return all;
      const next = [...all];
      [next[i], next[j]] = [next[j], next[i]];
      return next;
    });

  const remove = async (sp) => {
    const ok = await ask({
      title: "Remove sponsor?",
      message: (sp.name || "This sponsor") + " will come off the footer.",
      confirmLabel: "Remove",
      danger: true,
    });
    if (ok) setSponsors((all) => all.filter((x) => x.id !== sp.id));
  };

  /* Same rule the opponent marks use: stored inline here, uploaded to
     Storage in production. An SVG is encoded rather than kept as markup,
     which would leave a broken image behind. */
  const pickLogo = (id, file) => {
    if (!file) return;
    if (file.size > 400 * 1024) {
      ask({ title: "Image too large", message: "Sponsor logos must be under 400KB.", blocked: true });
      return;
    }
    const isSvg = file.type === "image/svg+xml" || /\\.svg$/i.test(file.name || "");
    const fr = new FileReader();
    fr.onload = () => setOne(id, { logo: isSvg ? svgDataUrl(fr.result) : fr.result });
    if (isSvg) fr.readAsText(file); else fr.readAsDataURL(file);
  };

  return (
    <>
      <p className="bsm" style={{ marginBottom: 18 }}>
        Shown in a band above the copyright line, in this order. A sponsor with no
        logo appears as its name.
      </p>

      {!list.length && (
        <div className="auempty">
          <p style={{ margin: 0, fontWeight: 600, color: "var(--au-text)" }}>No sponsors yet</p>
          <p className="bsm" style={{ margin: "6px 0 0" }}>
            The band stays hidden until there is at least one.
          </p>
        </div>
      )}

      <div style={{ display: "grid", gap: 14 }}>
        {list.map((sp, i) => (
          <article className="card" key={sp.id}>
            <div style={{ display: "flex", gap: 16, alignItems: "flex-start", flexWrap: "wrap" }}>
              <div style={{ flex: "0 0 auto", width: 132 }}>
                <div className="spprev">
                  {sp.logo
                    ? <img src={sp.logo} alt="" />
                    : <span className="bsm" style={{ color: "var(--au-faint)" }}>No logo</span>}
                </div>
                {sp.logo ? (
                  <button className="btn bGhost bSm" style={{ marginTop: 8, width: "100%" }}
                    onClick={() => setOne(sp.id, { logo: "" })}>Remove logo</button>
                ) : (
                  <label className="btn bGhost bSm" style={{ marginTop: 8, width: "100%", textAlign: "center", cursor: "pointer" }}>
                    Upload logo
                    <input type="file" accept="image/*" style={{ display: "none" }}
                      onChange={(e) => pickLogo(sp.id, e.target.files && e.target.files[0])} />
                  </label>
                )}
              </div>

              <div style={{ flex: "1 1 260px", minWidth: 0 }}>
                <div className="field">
                  <label className="h6">Name</label>
                  <input value={sp.name || ""} placeholder="Oakland Ice Center"
                    onChange={(e) => setOne(sp.id, { name: e.target.value })} />
                </div>
                <div className="field" style={{ marginTop: 12 }}>
                  <label className="h6">Link</label>
                  <input value={sp.url || ""} placeholder="https://…"
                    onChange={(e) => setOne(sp.id, { url: e.target.value })} />
                </div>
                <div style={{ display: "flex", gap: 8, marginTop: 14, flexWrap: "wrap" }}>
                  <button className="btn bGhost bSm" disabled={i === 0}
                    onClick={() => move(sp.id, -1)}>Move up</button>
                  <button className="btn bGhost bSm" disabled={i === list.length - 1}
                    onClick={() => move(sp.id, 1)}>Move down</button>
                  <button className="btn bGhost bSm" style={{ marginLeft: "auto" }}
                    onClick={() => remove(sp)}>Remove</button>
                </div>
              </div>
            </div>
          </article>
        ))}
      </div>

      <button className="btn bNavy bSm" style={{ marginTop: 18 }} onClick={add}>
        <IcPlusC size={15} /> Add sponsor
      </button>
    </>
  );
}

/* The alumni list. Same shape as the recruit inbox and deliberately plainer -""")

# The preview tile.
sub("""/* Sponsors — their own band, directly above the copyright line.""",
    """/* Console: the logo preview beside a sponsor's fields. Checkered so a mark
   on transparency is obviously on transparency. */
.spprev { height: 74px; border: 1px solid var(--au-line); border-radius: 8px;
  display: flex; align-items: center; justify-content: center; padding: 8px;
  background: #fff;
  background-image: linear-gradient(45deg, #EEF1F5 25%, transparent 25%),
    linear-gradient(-45deg, #EEF1F5 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #EEF1F5 75%),
    linear-gradient(-45deg, transparent 75%, #EEF1F5 75%);
  background-size: 12px 12px;
  background-position: 0 0, 0 6px, 6px -6px, -6px 0; }
.spprev img { max-height: 100%; max-width: 100%; object-fit: contain; }

/* Sponsors — their own band, directly above the copyright line.""")

io.open(p, 'w', encoding='utf-8').write(s)
print('console done')
