# -*- coding: utf-8 -*-
"""The console side: build a page, and arrange the bar.

Two editors.

PageBuilder is a page and its blocks. Add a block, fill it in, move it up or
down, take it out. The fields come from the block's own definition rather
than from a form written per type, so a new block type is one entry in
BLOCK_TYPES and nothing else - which is the only way a set of seven does not
become seven forms to keep in step.

Repeating blocks - cards, figures, questions - grow a row at a time and drop
empty ones on render, so there is no adding a card before knowing whether
there is a third one.

NavEditor is the bar. Move an item, rename it, hide it without deleting it,
nest it under a dropdown or lift it out. Add a page, a link out, or an empty
dropdown to put things in. A page and its nav entry are separate on purpose:
building a page does not put it in front of the public until somebody says
so, and taking it out of the bar does not delete the page.

Both write into the draft like every other editor here, so nothing reaches
the site until Publish.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ============================================================== the editors
sub("""/* ---------------- Custom theme builder ----------------""",
    """/* ---------------- Page builder ----------------
 *
 * The fields are read off the block's own definition rather than written per
 * type, because seven hand-written forms is seven things to keep in step
 * with seven renderers.
 */
function BlockFields({ block, set }) {
  const def = blockType(block.type);
  if (!def) return null;
  const fields = def[3] || [];

  const setItem = (key, i, k) => (e) => {
    const rows = [...(block[key] || [])];
    rows[i] = { ...(rows[i] || {}), [k]: e.target.value };
    set(key, rows);
  };
  const addRow = (key) => () => set(key, [...(block[key] || []), {}]);
  const dropRow = (key, i) => () => set(key, (block[key] || []).filter((_, j) => j !== i));

  const readImage = (key) => (e) => {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    const fr = new FileReader();
    fr.onload = () => set(key, fr.result);
    fr.readAsDataURL(file);
  };

  return (
    <div style={{ display: "grid", gap: 12 }}>
      {fields.map(([key, label, kind, cols]) => {
        if (kind === "list") {
          const rows = block[key] || [];
          return (
            <div className="field" key={key}>
              <label className="h6">{label}</label>
              {rows.map((row, i) => (
                <div className="aublockrow" key={i}>
                  {cols.map(([ck, clabel]) => (
                    <input key={ck} placeholder={clabel} value={row[ck] || ""}
                      onChange={setItem(key, i, ck)} />
                  ))}
                  <button className="btn bDanger" aria-label={"Remove " + label}
                    onClick={dropRow(key, i)}>\\u2715</button>
                </div>
              ))}
              <button className="btn bGhost bSm" style={{ marginTop: 8, justifySelf: "start" }}
                onClick={addRow(key)}>Add one</button>
            </div>
          );
        }
        if (kind === "image") {
          return (
            <div className="field" key={key}>
              <label className="h6">{label}</label>
              {block[key] && <img className="aublockimg" src={block[key]} alt="" />}
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <input type="file" accept="image/*" style={{ fontSize: 12 }}
                  onChange={readImage(key)} />
                {block[key] && (
                  <button className="btn bGhost bSm" onClick={() => set(key, "")}>Remove</button>
                )}
              </div>
            </div>
          );
        }
        return (
          <div className="field" key={key}>
            <label className="h6">{label}</label>
            {kind === "markdown" || kind === "text"
              ? <textarea rows={kind === "markdown" ? 10 : 3} value={block[key] || ""}
                  onChange={(e) => set(key, e.target.value)} />
              : <input value={block[key] || ""} onChange={(e) => set(key, e.target.value)} />}
          </div>
        );
      })}
    </div>
  );
}

function PageBuilder({ site, setDraft, pageId, onGone }) {
  const ask = useAsk();
  const pages = site.pages || [];
  const page = pages.find((p) => p.id === pageId);
  const [adding, setAdding] = useState(false);

  const write = (fn) => setDraft((st) => ({
    ...st,
    pages: (st.pages || []).map((p) => (p.id === pageId ? fn(p) : p)),
  }));

  if (!page) {
    return (
      <section className="card">
        <p className="h6" style={{ marginBottom: 6 }}>Page not found</p>
        <p className="auhint" style={{ margin: 0 }}>It may have been deleted.</p>
      </section>
    );
  }

  const blocks = page.blocks || [];
  const setBlock = (id) => (key, value) => write((p) => ({
    ...p, blocks: (p.blocks || []).map((b) => (b.id === id ? { ...b, [key]: value } : b)),
  }));
  const move = (i, by) => write((p) => {
    const list = [...(p.blocks || [])];
    const j = i + by;
    if (j < 0 || j >= list.length) return p;
    [list[i], list[j]] = [list[j], list[i]];
    return { ...p, blocks: list };
  });
  const remove = async (b) => {
    const def = blockType(b.type);
    const ok = await ask({
      title: "Remove this block?",
      message: (def ? def[1] : "Block") + " and everything written in it.",
      confirmLabel: "Remove", danger: true,
    });
    if (ok) write((p) => ({ ...p, blocks: (p.blocks || []).filter((x) => x.id !== b.id) }));
  };
  const add = (type) => {
    write((p) => ({ ...p, blocks: [...(p.blocks || []), { id: uid(), type }] }));
    setAdding(false);
  };

  const deletePage = async () => {
    const ok = await ask({
      title: "Delete this page?",
      message: (page.title || "This page") + " and everything on it. Its place in the "
        + "menu bar goes too.",
      confirmLabel: "Delete", danger: true,
    });
    if (!ok) return;
    setDraft((st) => ({
      ...st,
      pages: (st.pages || []).filter((p) => p.id !== pageId),
      /* A nav entry pointing at a deleted page is a link to nowhere. */
      nav: (st.nav || []).map((it) => (it.items
        ? { ...it, items: it.items.filter((c) => c.view !== pageView(pageId)) } : it))
        .filter((it) => (it.items ? true : it.view !== pageView(pageId))),
    }));
    onGone();
  };

  return (
    <div style={{ display: "grid", gap: 18, maxWidth: 720 }}>
      <section className="card">
        <div className="field">
          <label className="h6">Page title</label>
          <input value={page.title || ""}
            onChange={(e) => write((p) => ({ ...p, title: e.target.value }))} />
        </div>
        <p className="auhint" style={{ margin: "10px 0 0" }}>
          The title is what the menu bar offers it as until you rename it there.
          A page is not on the site until it is in the bar.
        </p>
      </section>

      {blocks.map((b, i) => {
        const def = blockType(b.type);
        return (
          <section className="card" key={b.id}>
            <div className="aublockhead">
              <div>
                <p className="h6" style={{ margin: 0 }}>{def ? def[1] : b.type}</p>
                {def && <p className="bsm" style={{ margin: "2px 0 0", color: "var(--au-faint)" }}>{def[2]}</p>}
              </div>
              <div style={{ display: "flex", gap: 6 }}>
                <button className="btn bGhost bSm" onClick={() => move(i, -1)}
                  disabled={i === 0} title="Move up">\\u2191</button>
                <button className="btn bGhost bSm" onClick={() => move(i, 1)}
                  disabled={i === blocks.length - 1} title="Move down">\\u2193</button>
                <button className="btn bGhost bSm" onClick={() => remove(b)} title="Remove">\\u2715</button>
              </div>
            </div>
            <div style={{ marginTop: 14 }}>
              <BlockFields block={b} set={setBlock(b.id)} />
            </div>
          </section>
        );
      })}

      {!blocks.length && (
        <div className="auempty">
          <p style={{ margin: 0, fontWeight: 600, color: "var(--au-text)" }}>No blocks yet</p>
          <p className="bsm" style={{ margin: "6px 0 0" }}>
            A page is a stack of blocks. Add the first one below.
          </p>
        </div>
      )}

      {adding ? (
        <section className="card">
          <p className="h6" style={{ marginBottom: 10 }}>Add a block</p>
          <div className="aublockpick">
            {BLOCK_TYPES.map(([t, label, hint]) => (
              <button className="aublockopt" key={t} onClick={() => add(t)}>
                <span className="aublockoptname">{label}</span>
                <span className="aublockopthint">{hint}</span>
              </button>
            ))}
          </div>
          <button className="btn bGhost bSm" style={{ marginTop: 12 }}
            onClick={() => setAdding(false)}>Cancel</button>
        </section>
      ) : (
        <div style={{ display: "flex", gap: 10 }}>
          <button className="btn bNavy" onClick={() => setAdding(true)}>+ Add block</button>
          <button className="btn bGhost" style={{ marginLeft: "auto" }}
            onClick={deletePage}>Delete page</button>
        </div>
      )}
    </div>
  );
}

/* ---------------- The menu bar ----------------
 *
 * A page and its place in the bar are separate on purpose: building a page
 * does not put it in front of the public, and taking it out of the bar does
 * not delete it.
 */
const NAV_DESTINATIONS = [
  ["home", "Home"], ["schedule", "Schedule"], ["roster", "Roster"],
  ["prospects", "Recruits"], ["staff", "Hockey Ops Staff"], ["volunteers", "Volunteers"],
  ["stats", "Stats"], ["newsindex", "News"], ["venue", "Venue"], ["alumni", "Alumni"],
  ["recruit", "Interest form"], ["tickets", "Tickets"],
];

function NavEditor({ site, setDraft }) {
  const ask = useAsk();
  const pages = site.pages || [];
  const bar = Array.isArray(site.nav) && site.nav.length ? site.nav : DEFAULT_NAV;
  const [addTo, setAddTo] = useState(null);

  const write = (next) => setDraft((st) => ({ ...st, nav: next }));

  /* Every item, flattened with where it sits, so a move is arithmetic on one
     list rather than four cases about parents. */
  const setAt = (parentId, fn) => write(bar.map((it) => (
    parentId && it.id === parentId ? { ...it, items: fn(it.items || []) }
      : it)));

  const moveTop = (i, by) => {
    const list = [...bar];
    const j = i + by;
    if (j < 0 || j >= list.length) return;
    [list[i], list[j]] = [list[j], list[i]];
    write(list);
  };
  const moveChild = (parentId, i, by) => setAt(parentId, (items) => {
    const list = [...items];
    const j = i + by;
    if (j < 0 || j >= list.length) return items;
    [list[i], list[j]] = [list[j], list[i]];
    return list;
  });

  const rename = (parentId, id, label) => (parentId
    ? setAt(parentId, (items) => items.map((c) => (c.id === id ? { ...c, label } : c)))
    : write(bar.map((it) => (it.id === id ? { ...it, label } : it))));

  const toggleHide = (parentId, id) => (parentId
    ? setAt(parentId, (items) => items.map((c) => (c.id === id ? { ...c, hidden: !c.hidden } : c)))
    : write(bar.map((it) => (it.id === id ? { ...it, hidden: !it.hidden } : it))));

  const drop = async (parentId, item) => {
    const ok = await ask({
      title: "Remove from the menu?",
      message: (item.label || "This item") + (item.items && item.items.length
        ? " and the " + item.items.length + " items under it."
        : ". The page itself is not deleted."),
      confirmLabel: "Remove", danger: true,
    });
    if (!ok) return;
    if (parentId) setAt(parentId, (items) => items.filter((c) => c.id !== item.id));
    else write(bar.filter((it) => it.id !== item.id));
  };

  /* Lifting a child to the top level and pushing a top-level item into the
     dropdown above it: the two moves the arrows cannot make. */
  const lift = (parentId, item) => {
    const at = bar.findIndex((it) => it.id === parentId);
    const next = bar.map((it) => (it.id === parentId
      ? { ...it, items: (it.items || []).filter((c) => c.id !== item.id) } : it));
    next.splice(at + 1, 0, item);
    write(next);
  };
  const nest = (i) => {
    const item = bar[i];
    /* The nearest dropdown above it, which is where "indent" means. */
    let host = -1;
    for (let j = i - 1; j >= 0; j--) if (bar[j].items) { host = j; break; }
    if (host < 0) return;
    write(bar
      .map((it, j) => (j === host ? { ...it, items: [...(it.items || []), item] } : it))
      .filter((_, j) => j !== i));
  };

  const addItem = (parentId, made) => {
    if (parentId) setAt(parentId, (items) => [...items, made]);
    else write([...bar, made]);
    setAddTo(null);
  };

  const Adder = ({ parentId }) => (
    <section className="card aunavadd">
      <p className="h6" style={{ marginBottom: 8 }}>
        Add to {parentId ? "this dropdown" : "the bar"}
      </p>
      <div className="field">
        <label className="h6">A page of the site</label>
        <select value="" onChange={(e) => e.target.value && addItem(parentId, {
          id: uid(), label: (NAV_DESTINATIONS.find(([v]) => v === e.target.value) || [])[1]
            || e.target.value, view: e.target.value })}>
          <option value="">\\u2014 pick one \\u2014</option>
          {NAV_DESTINATIONS.map(([v, label]) => <option key={v} value={v}>{label}</option>)}
        </select>
      </div>
      {pages.length > 0 && (
        <div className="field" style={{ marginTop: 10 }}>
          <label className="h6">A page you built</label>
          <select value="" onChange={(e) => e.target.value && addItem(parentId, {
            id: uid(),
            label: (pages.find((p) => p.id === e.target.value) || {}).title || "Untitled",
            view: pageView(e.target.value) })}>
            <option value="">\\u2014 pick one \\u2014</option>
            {pages.map((p) => <option key={p.id} value={p.id}>{p.title || "Untitled"}</option>)}
          </select>
        </div>
      )}
      <div className="field" style={{ marginTop: 10 }}>
        <label className="h6">A link out</label>
        <input placeholder="https://\\u2026" onKeyDown={(e) => {
          if (e.key !== "Enter") return;
          const href = e.currentTarget.value.trim();
          if (href) addItem(parentId, { id: uid(), label: "New link", href });
        }} />
        <p className="bsm" style={{ marginTop: 5, color: "var(--au-faint)" }}>
          Enter to add, then rename it above.
        </p>
      </div>
      {!parentId && (
        <button className="btn bGhost bSm" style={{ marginTop: 12 }}
          onClick={() => addItem(null, { id: uid(), label: "New menu", items: [] })}>
          Add an empty dropdown
        </button>
      )}
      <button className="btn bGhost bSm" style={{ marginTop: 12, marginLeft: 8 }}
        onClick={() => setAddTo(null)}>Cancel</button>
    </section>
  );

  const Row = ({ item, parentId, i, count }) => (
    <div className={"aunavrow" + (item.hidden ? " off" : "") + (parentId ? " child" : "")}>
      <input className="aunavlabel" value={item.label || ""}
        onChange={(e) => rename(parentId, item.id, e.target.value)} />
      <span className="aunavwhat">
        {item.items ? "dropdown" : item.href ? "link out"
          : viewPageId(item.view) ? "built page" : "page"}
      </span>
      <button className="btn bGhost bSm" title="Move up" disabled={i === 0}
        onClick={() => (parentId ? moveChild(parentId, i, -1) : moveTop(i, -1))}>\\u2191</button>
      <button className="btn bGhost bSm" title="Move down" disabled={i === count - 1}
        onClick={() => (parentId ? moveChild(parentId, i, 1) : moveTop(i, 1))}>\\u2193</button>
      {parentId
        ? <button className="btn bGhost bSm" title="Move out of this dropdown"
            onClick={() => lift(parentId, item)}>\\u2190</button>
        : <button className="btn bGhost bSm" title="Move into the dropdown above"
            disabled={item.items || !bar.slice(0, i).some((x) => x.items)}
            onClick={() => nest(i)}>\\u2192</button>}
      <button className="btn bGhost bSm" title={item.hidden ? "Show it" : "Hide it"}
        onClick={() => toggleHide(parentId, item.id)}>{item.hidden ? "Hidden" : "Shown"}</button>
      <button className="btn bDanger" title="Remove from the menu"
        onClick={() => drop(parentId, item)}>\\u2715</button>
    </div>
  );

  return (
    <div style={{ display: "grid", gap: 18, maxWidth: 760 }}>
      <section className="card">
        <p className="h6" style={{ marginBottom: 6 }}>Menu bar</p>
        <p className="auhint" style={{ marginTop: 0 }}>
          The bar across the top of the public site, and the same list the phone
          menu reads. Hiding an item leaves it here; removing it does not delete
          the page it points at.
        </p>
        <div className="aunavlist">
          {bar.map((item, i) => (
            <div key={item.id}>
              <Row item={item} parentId={null} i={i} count={bar.length} />
              {item.items && (
                <>
                  {(item.items || []).map((c, j) => (
                    <Row key={c.id} item={c} parentId={item.id} i={j} count={item.items.length} />
                  ))}
                  <button className="btn bGhost bSm aunavaddchild"
                    onClick={() => setAddTo(item.id)}>+ Add to {item.label}</button>
                </>
              )}
            </div>
          ))}
        </div>
        <div style={{ display: "flex", gap: 10, marginTop: 14 }}>
          <button className="btn bNavy bSm" onClick={() => setAddTo("top")}>+ Add to the bar</button>
          <button className="btn bGhost bSm" style={{ marginLeft: "auto" }}
            onClick={async () => {
              const ok = await ask({
                title: "Put the menu back?",
                message: "Back to Home, Schedule, Team, Stats, News and More as it ships.",
                confirmLabel: "Reset", danger: true,
              });
              if (ok) write(DEFAULT_NAV);
            }}>Reset to default</button>
        </div>
      </section>

      {addTo && <Adder parentId={addTo === "top" ? null : addTo} />}
    </div>
  );
}

/* ---------------- Custom theme builder ----------------""")

io.open(p, 'w', encoding='utf-8').write(s)
print('page builder and nav editor written')
