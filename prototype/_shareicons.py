# -*- coding: utf-8 -*-
"""More headlines drops the condensed tag, and sharing becomes round icons.

Two things.

The tag on each More headlines row was still Barlow Condensed, uppercased
and letter-spaced - the same treatment taken off the story's own labels a
change ago, missed because it lives in a different rule with a different
name. Body face, written case, and the tag cased for reading like the one at
the top of the page.

And the share row becomes what was asked for: round icon buttons rather than
pills with words in them. Thirty-four pixels, which is the size in the
markup that was sent.

That markup could not be used directly - it is <use> pointing into a sprite
sheet, so it carries the names of the icons and none of their artwork, and
the artwork it points at is somebody else's. These are the site's own
glyphs, drawn in the shape those references describe.

LinkedIn joins them, because it was in the set and had no icon here.
Instagram stays out: it has no share URL at all, so a share-to-Instagram
button either opens the app with nothing attached or does nothing, and Copy
link is the honest version of it.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ======================================================= 1. More headlines
sub(""".artmoretag { font-family: var(--disp); font-weight: 600; font-size: 11px; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--blue); }""",
    """/* The same treatment the story's own labels lost: body face, written case.
   Missed the first time because it lives in its own rule under another
   name. */
.artmoretag { font-weight: 700; font-size: 12px; letter-spacing: 0; color: var(--blue); }""")

sub("""                    <span className="artmoretag">{n.tag}</span>""",
    """                    <span className="artmoretag">{casedTag(n.tag)}</span>""")

# ============================================== 2. LinkedIn, and the round row
sub("""const IcFacebook = (p) => <Ic {...p} d={<path d="M14.5 8.5h2.5M14.5 21V8.6c0-1.7 1-2.6 2.6-2.6H18M10.5 12.5h6" />} />;""",
    """const IcFacebook = (p) => <Ic {...p} d={<path d="M14.5 8.5h2.5M14.5 21V8.6c0-1.7 1-2.6 2.6-2.6H18M10.5 12.5h6" />} />;
const IcLinkedIn = (p) => <Ic {...p} d={<><rect x="3.5" y="3.5" width="17" height="17" rx="3" /><path d="M8 10.5V16M8 7.6v.01M12 16v-3.4a2 2 0 0 1 4 0V16" /></>} />;""")

sub("""const SHARE_TARGETS = [
  ["x", "X", IcX, (u, t) => "https://x.com/intent/post?url=" + encodeURIComponent(u) + "&text=" + encodeURIComponent(t)],
  ["facebook", "Facebook", IcFacebook, (u) => "https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(u)],
];""",
    """const SHARE_TARGETS = [
  ["x", "X", IcX, (u, t) => "https://x.com/intent/post?url=" + encodeURIComponent(u) + "&text=" + encodeURIComponent(t)],
  ["facebook", "Facebook", IcFacebook, (u) => "https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(u)],
  ["linkedin", "LinkedIn", IcLinkedIn, (u) => "https://www.linkedin.com/sharing/share-offsite/?url=" + encodeURIComponent(u)],
];""")

sub("""      <div className="artsharebtns">
        {native && (
          <button className="sharebtn" onClick={() => navigator.share({ title, url }).catch(() => {})}>
            <IcShare size={15} /> Share
          </button>
        )}
        {SHARE_TARGETS.map(([key, label, Icon, href]) => (
          <a key={key} className="sharebtn" href={href(url, title)}
            target="_blank" rel="noreferrer noopener" aria-label={"Share on " + label}>
            <Icon size={15} /> {label}
          </a>
        ))}
        <a className="sharebtn"
          href={"mailto:?subject=" + encodeURIComponent(title) + "&body=" + encodeURIComponent(url)}
          aria-label="Share by email">
          <IcMail size={15} /> Email
        </a>
        <button className={"sharebtn" + (copied ? " ok" : "")} onClick={copy}
          aria-label="Copy link to this story">
          {copied ? <IcCheck size={15} /> : <IcLink size={15} />}
          {copied ? "Copied" : "Copy link"}
        </button>
      </div>""",
    """      <div className="artsharebtns">
        {/* Icon only, so each button says what it is by its mark and to a
            screen reader by its label. */}
        {native && (
          <button className="sharebtn" title="Share" aria-label="Share this story"
            onClick={() => navigator.share({ title, url }).catch(() => {})}>
            <IcShare size={17} />
          </button>
        )}
        {SHARE_TARGETS.map(([key, label, Icon, href]) => (
          <a key={key} className="sharebtn" href={href(url, title)} title={label}
            target="_blank" rel="noreferrer noopener" aria-label={"Share on " + label}>
            <Icon size={17} />
          </a>
        ))}
        <a className="sharebtn" title="Email"
          href={"mailto:?subject=" + encodeURIComponent(title) + "&body=" + encodeURIComponent(url)}
          aria-label="Share by email">
          <IcMail size={17} />
        </a>
        <button className={"sharebtn" + (copied ? " ok" : "")} onClick={copy}
          title="Copy link" aria-label="Copy link to this story">
          {copied ? <IcCheck size={17} /> : <IcLink size={17} />}
          {/* Said rather than guessed at: a button that changes its own icon
              and nothing else leaves you wondering whether it worked. */}
          <span className="sharepop" role="status">{copied ? "Link copied" : ""}</span>
        </button>
      </div>""")

sub(""".sharebtn { display: inline-flex; align-items: center; gap: 7px; padding: 7px 14px;""",
    """/* Round, thirty-four across, the shape the reference markup describes. Its
   own artwork is a sprite reference rather than paths, so these are the
   site's glyphs in that shape. */
.sharebtn { position: relative; width: 34px; height: 34px; padding: 0;
  display: inline-flex; align-items: center; justify-content: center; border-radius: 999px;""")

sub(""".artsharebtns { display: flex; flex-wrap: wrap; gap: 8px; }""",
    """.artsharebtns { display: flex; flex-wrap: wrap; gap: 8px; }
/* Above the button that was pressed, and only while it has something to
   say - an empty status node should not reserve a box. */
.sharepop { position: absolute; bottom: calc(100% + 8px); left: 50%; transform: translateX(-50%);
  background: var(--ink); color: #fff; font-size: 11.5px; font-weight: 700;
  padding: 4px 9px; border-radius: 6px; white-space: nowrap; pointer-events: none; }
.sharepop:empty { display: none; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('round share icons; more headlines de-shouted')
