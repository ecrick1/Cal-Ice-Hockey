# -*- coding: utf-8 -*-
"""The real marks, from the files that were sent.

X, Facebook and LinkedIn as supplied. The last set were the site's own
glyphs drawn in roughly the right shape, because what had been pasted was a
sprite reference carrying names and no paths; these are the paths.

They are the Negative cut, which means each is one filled shape with the
letter knocked out of it rather than a letter drawn on top - Facebook is a
disc with an f-shaped hole, LinkedIn a rounded square with the logo cut out.
So the mark is the button: filled in navy, the hole shows the page through
it, and there is nothing for a border or a background to add. Drawing them
inside a bordered circle would have put a shape inside a shape.

X arrives as the bare glyph with no container, so it gets the disc the other
two bring with them, and the letter in white rather than knocked out - the
same reading, built the other way round because that is what the file
allows.

Email and Copy link are not brands and have no supplied mark. They take the
same disc so the row is five of one thing rather than three and two.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


X_PATH = ("M36.6526 3.8078H43.3995L28.6594 20.6548L46 43.5797H32.4225L21.7881 "
          "29.6759L9.61989 43.5797H2.86886L18.6349 25.56L2 3.8078H15.9222L25.5348 "
          "16.5165L36.6526 3.8078ZM34.2846 39.5414H38.0232L13.8908 7.63406H9.87892L34.2846 39.5414Z")

FB_PATH = ("M24 0C10.7453 0 0 10.7453 0 24C0 35.255 7.74912 44.6995 18.2026 "
           "47.2934V31.3344H13.2538V24H18.2026V20.8397C18.2026 12.671 21.8995 8.8848 "
           "29.9194 8.8848C31.44 8.8848 34.0637 9.18336 35.137 9.48096V16.129C34.5706 "
           "16.0694 33.5866 16.0397 32.3645 16.0397C28.4294 16.0397 26.9088 17.5306 "
           "26.9088 21.4061V24H34.7482L33.4013 31.3344H26.9088V47.8243C38.7926 46.3891 "
           "48.001 36.2707 48.001 24C48 10.7453 37.2547 0 24 0Z")

LI_PATH = ("M44.4469 0H3.54375C1.58437 0 0 1.54688 0 3.45938V44.5312C0 46.4437 1.58437 "
           "48 3.54375 48H44.4469C46.4062 48 48 46.4438 48 44.5406V3.45938C48 1.54688 "
           "46.4062 0 44.4469 0ZM14.2406 40.9031H7.11563V17.9906H14.2406V40.9031ZM10.6781 "
           "14.8688C8.39062 14.8688 6.54375 13.0219 6.54375 10.7437C6.54375 8.46562 "
           "8.39062 6.61875 10.6781 6.61875C12.9563 6.61875 14.8031 8.46562 14.8031 "
           "10.7437C14.8031 13.0125 12.9563 14.8688 10.6781 14.8688ZM40.9031 "
           "40.9031H33.7875V29.7656C33.7875 27.1125 33.7406 23.6906 30.0844 23.6906C26.3812 "
           "23.6906 25.8187 26.5875 25.8187 29.5781V40.9031H18.7125V17.9906H25.5375V21.1219H25.6312C26.5781 "
           "19.3219 28.9031 17.4188 32.3625 17.4188C39.5719 17.4188 40.9031 22.1625 40.9031 28.3313V40.9031Z")

icons = '''
/* ---------------- Share marks ----------------
 *
 * The brand files as delivered, in their Negative cut: one filled shape with
 * the letter knocked out of it, so what shows through the hole is whatever
 * is behind. Filled in the current colour, that makes the mark its own
 * button - a disc for Facebook, a rounded square for LinkedIn - and leaves a
 * border or a background nothing to do but draw a shape around a shape.
 *
 * X comes as the bare glyph with no container, so it is given the disc the
 * other two bring with them and the letter is painted white instead of cut
 * out. Same reading, built the other way round, because that is what the
 * file allows.
 */
const ShareMark = ({ size = 34, children }) => (
  <svg viewBox="0 0 48 48" width={size} height={size} fill="none" aria-hidden="true"
    focusable="false">{children}</svg>
);

const ShX = (p) => (
  <ShareMark {...p}>
    <circle cx="24" cy="24" r="24" fill="currentColor" />
    <g transform="translate(24 24) scale(0.62) translate(-24 -24)">
      <path d="__X__" fill="#fff" />
    </g>
  </ShareMark>
);

const ShFacebook = (p) => (
  <ShareMark {...p}><path d="__FB__" fill="currentColor" /></ShareMark>
);

const ShLinkedIn = (p) => (
  <ShareMark {...p}><path d="__LI__" fill="currentColor" /></ShareMark>
);

/* Not brands, and no supplied mark - the same disc, so the row reads as five
   of one thing rather than three and two. */
const ShMail = (p) => (
  <ShareMark {...p}>
    <circle cx="24" cy="24" r="24" fill="currentColor" />
    <g stroke="#fff" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round">
      <rect x="13" y="16.5" width="22" height="15" rx="2.5" />
      <path d="M13.8 18.2 24 26l10.2-7.8" />
    </g>
  </ShareMark>
);

const ShLink = (p) => (
  <ShareMark {...p}>
    <circle cx="24" cy="24" r="24" fill="currentColor" />
    <g stroke="#fff" strokeWidth="2.8" strokeLinecap="round">
      <path d="M21 27a5 5 0 0 0 7 0l4-4a5 5 0 0 0-7-7l-1.6 1.6" />
      <path d="M27 21a5 5 0 0 0-7 0l-4 4a5 5 0 0 0 7 7l1.6-1.6" />
    </g>
  </ShareMark>
);

const ShCheck = (p) => (
  <ShareMark {...p}>
    <circle cx="24" cy="24" r="24" fill="currentColor" />
    <path d="M15 24.5 21.5 31 33 18.5" stroke="#fff" strokeWidth="3.2"
      strokeLinecap="round" strokeLinejoin="round" />
  </ShareMark>
);

'''
icons = icons.replace("__X__", X_PATH).replace("__FB__", FB_PATH).replace("__LI__", LI_PATH)

sub("""/* Instagram is deliberately absent: it has no share URL. Every "share to
   Instagram" button on the web either opens the app with nothing attached or
   quietly does nothing, and Copy link is the honest version of it. */""",
    icons + """/* Instagram is deliberately absent: it has no share URL. Every "share to
   Instagram" button on the web either opens the app with nothing attached or
   quietly does nothing, and Copy link is the honest version of it. */""")

sub("""  ["x", "X", IcX, (u, t) => "https://x.com/intent/post?url=" + encodeURIComponent(u) + "&text=" + encodeURIComponent(t)],
  ["facebook", "Facebook", IcFacebook, (u) => "https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(u)],
  ["linkedin", "LinkedIn", IcLinkedIn, (u) => "https://www.linkedin.com/sharing/share-offsite/?url=" + encodeURIComponent(u)],""",
    """  ["x", "X", ShX, (u, t) => "https://x.com/intent/post?url=" + encodeURIComponent(u) + "&text=" + encodeURIComponent(t)],
  ["facebook", "Facebook", ShFacebook, (u) => "https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(u)],
  ["linkedin", "LinkedIn", ShLinkedIn, (u) => "https://www.linkedin.com/sharing/share-offsite/?url=" + encodeURIComponent(u)],""")

# the row: the mark is the button
sub("""        {SHARE_TARGETS.map(([key, label, Icon, href]) => (
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
          {copied ? <IcCheck size={17} /> : <IcLink size={17} />}""",
    """        {SHARE_TARGETS.map(([key, label, Icon, href]) => (
          <a key={key} className="sharebtn" href={href(url, title)} title={label}
            target="_blank" rel="noreferrer noopener" aria-label={"Share on " + label}>
            <Icon size={34} />
          </a>
        ))}
        <a className="sharebtn" title="Email"
          href={"mailto:?subject=" + encodeURIComponent(title) + "&body=" + encodeURIComponent(url)}
          aria-label="Share by email">
          <ShMail size={34} />
        </a>
        <button className={"sharebtn" + (copied ? " ok" : "")} onClick={copy}
          title="Copy link" aria-label="Copy link to this story">
          {copied ? <ShCheck size={34} /> : <ShLink size={34} />}""")

sub("""/* Round, thirty-four across, the shape the reference markup describes. Its
   own artwork is a sprite reference rather than paths, so these are the
   site's glyphs in that shape. */
.sharebtn { position: relative; width: 34px; height: 34px; padding: 0;
  display: inline-flex; align-items: center; justify-content: center; border-radius: 999px;
  border: 1px solid var(--border); border-radius: 999px; background: #fff; cursor: pointer;
  font: inherit; font-size: 13.5px; font-weight: 700; color: var(--deep);
  text-decoration: none; line-height: 1; }
.sharebtn:hover { border-color: var(--blue); color: var(--blue); }""",
    """/* The mark is the button. Each is a filled shape with its letter knocked
   out, so a border or a background would only draw a shape around a shape. */
.sharebtn { position: relative; width: 34px; height: 34px; padding: 0;
  display: inline-flex; align-items: center; justify-content: center;
  border: 0; background: none; cursor: pointer; color: var(--deep);
  text-decoration: none; line-height: 0; opacity: 0.9;
  transition: opacity 0.15s ease, color 0.15s ease; }
.sharebtn:hover { color: var(--blue); opacity: 1; }""")

sub(""".sharebtn.ok, .sharebtn.ok:hover { border-color: var(--blue); background: var(--blue); color: #fff; }""",
    """.sharebtn.ok, .sharebtn.ok:hover { color: var(--blue); opacity: 1; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('the real marks are in')
