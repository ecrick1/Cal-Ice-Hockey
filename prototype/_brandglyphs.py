# -*- coding: utf-8 -*-
"""The supplied marks, as glyphs in the header and glyphs in a circle on a story.

Three more files: Facebook as a bare f rather than a disc with the f cut out
of it, TikTok, and YouTube. With a bare f the whole share row can be built
one way - a filled circle with the letter on it - instead of two marks
bringing their own container and one borrowing a drawn one.

LinkedIn is still the Negative cut and still a rounded square with the logo
knocked out, so it is masked into a circle: the circle is painted, and the
logo alone is cut back out of it. Same reading as the others, arrived at
from the one shape the file gives.

YouTube is a rounded rectangle with the play triangle knocked out. In the
header it keeps that shape and the triangle is masked rather than painted
white, so the navy behind it shows at rest and the gold shows on hover -
a white triangle would have been a white triangle on gold.

The header keeps glyphs rather than circles. Its icons sit on navy and gain
a gold disc when hovered; putting each mark in a disc of its own would have
been a disc inside a disc, which is the mistake the share row just had
taken out of it.

Instagram is the one mark with no file, so it keeps the drawn outline. It is
lighter than the five beside it and will stay that way until there is an
Instagram file to replace it with.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


FB = ("M24.645 40.6953V70H11.1834V40.6953H0V28.8129H11.1834V24.4896C11.1834 8.43935 "
      "17.8883 0 32.0747 0C36.4238 0 37.5111 0.698965 39.8927 1.26849V13.0215C37.2263 "
      "12.5555 36.4756 12.2966 33.7056 12.2966C30.4179 12.2966 28.6575 13.2286 27.0525 "
      "15.0666C25.4475 16.9046 24.645 20.0888 24.645 24.645V28.8388H39.8927L35.8025 "
      "40.7212H24.645V40.6953Z")

TT = ("M44.5893 2.66285L42.9004 0H32.6802V23.9831L32.6454 47.4092C32.6628 47.5833 32.6802 "
      "47.7747 32.6802 47.9488C32.6802 53.814 27.9097 58.6002 22.0248 58.6002C16.1399 "
      "58.6002 11.3693 53.8314 11.3693 47.9488C11.3693 42.0835 16.1399 37.2974 22.0248 "
      "37.2974C23.2435 37.2974 24.4275 37.5236 25.5244 37.9065V26.2108C24.3927 26.0194 "
      "23.2261 25.915 22.0248 25.915C9.88939 25.9324 0 35.818 0 47.9662C0 60.1144 8.88939 "
      "70 22.0422 70C34.195 70 44.0844 60.1144 44.0844 47.9662V20.1019C48.4893 24.5052 "
      "54.1827 28.8041 60.4854 30.179V18.2223C53.643 15.1939 46.8353 6.24814 44.5893 2.66285Z")
# the file's own value, restored verbatim
TT = TT.replace("C0 60.1144 8.88939 70", "C0 60.1144 9.88939 70")

YT_BOX = ("M74.5024 60H14.4975C6.46861 60 0 52.8994 0 44.1657V15.8343C0 7.06509 6.50112 0 "
          "14.4975 0H74.5024C82.5313 0 88.9999 7.10059 88.9999 15.8343V44.1657C89.0324 "
          "52.9349 82.5313 60 74.5024 60Z")
YT_TRI = "M60.2426 29.5562L35 15V44.1124L60.2426 29.5562Z"

LI = ("M44.4469 0H3.54375C1.58437 0 0 1.54688 0 3.45938V44.5312C0 46.4437 1.58437 48 "
      "3.54375 48H44.4469C46.4062 48 48 46.4438 48 44.5406V3.45938C48 1.54688 46.4062 0 "
      "44.4469 0ZM14.2406 40.9031H7.11563V17.9906H14.2406V40.9031ZM10.6781 14.8688C8.39062 "
      "14.8688 6.54375 13.0219 6.54375 10.7437C6.54375 8.46562 8.39062 6.61875 10.6781 "
      "6.61875C12.9563 6.61875 14.8031 8.46562 14.8031 10.7437C14.8031 13.0125 12.9563 "
      "14.8688 10.6781 14.8688ZM40.9031 40.9031H33.7875V29.7656C33.7875 27.1125 33.7406 "
      "23.6906 30.0844 23.6906C26.3812 23.6906 25.8187 26.5875 25.8187 29.5781V40.9031H18.7125"
      "V17.9906H25.5375V21.1219H25.6312C26.5781 19.3219 28.9031 17.4188 32.3625 17.4188C39.5719 "
      "17.4188 40.9031 22.1625 40.9031 28.3313V40.9031Z")

X = ("M36.6526 3.8078H43.3995L28.6594 20.6548L46 43.5797H32.4225L21.7881 29.6759L9.61989 "
     "43.5797H2.86886L18.6349 25.56L2 3.8078H15.9222L25.5348 16.5165L36.6526 3.8078ZM34.2846 "
     "39.5414H38.0232L13.8908 7.63406H9.87892L34.2846 39.5414Z")

block = '''
/* ---------------- Brand marks ----------------
 *
 * The delivered artwork, each file in its own box, placed into a common 48
 * square so marks drawn at different scales sit at the same optical size.
 * `fit` centres a glyph that starts at the origin; the two that do not get
 * their own transform.
 */
const fit = (w, h, target) => {
  const k = target / h;
  return "translate(" + ((48 - w * k) / 2) + " " + ((48 - target) / 2) + ") scale(" + k + ")";
};

const G_FACEBOOK = { d: "__FB__", t: fit(39.9, 70, 24) };
const G_TIKTOK = { d: "__TT__", t: fit(60.5, 70, 24) };
/* X sits inset in its own 48 box rather than filling it. */
const G_X = { d: "__X__", t: "translate(24 24) scale(0.5) translate(-24 -24)" };

const Svg48 = ({ size, children, extra }) => (
  <svg viewBox="0 0 48 48" width={size} height={size} fill="none" aria-hidden="true"
    focusable="false" {...extra}>{children}</svg>
);

/* A glyph on its own, in the current colour - what the header wants, where
   the icons sit on navy and the disc is the hover state. */
const Glyph = ({ g, size = 18 }) => (
  <Svg48 size={size}><g transform={g.t}><path d={g.d} fill="currentColor" /></g></Svg48>
);

const BrFacebook = (p) => <Glyph {...p} g={G_FACEBOOK} />;
const BrTikTok = (p) => <Glyph {...p} g={G_TIKTOK} />;
const BrX = (p) => <Glyph {...p} g={G_X} />;

/* YouTube is a rounded rectangle with the play triangle knocked out of it.
   Masked rather than painted white, so what shows through the triangle is
   the navy at rest and the gold on hover. */
const BrYouTube = ({ size = 18 }) => (
  <Svg48 size={size}>
    <mask id="ytmask" maskUnits="userSpaceOnUse" x="0" y="0" width="48" height="48">
      <g transform={fit(89, 60, 28)}>
        <path d="__YTBOX__" fill="#fff" />
        <path d="__YTTRI__" fill="#000" />
      </g>
    </mask>
    <rect width="48" height="48" fill="currentColor" mask="url(#ytmask)" />
  </Svg48>
);

/* The mark in a filled circle, the letter cut out of it - what a story's
   share row wants, on white. */
const CircleMark = ({ g, size = 22 }) => (
  <Svg48 size={size}>
    <mask id={"cm" + g.id} maskUnits="userSpaceOnUse" x="0" y="0" width="48" height="48">
      <circle cx="24" cy="24" r="24" fill="#fff" />
      <g transform={g.t}><path d={g.d} fill="#000" /></g>
    </mask>
    <circle cx="24" cy="24" r="24" fill="currentColor" mask={"url(#cm" + g.id + ")"} />
  </Svg48>
);

const ShX = (p) => <CircleMark {...p} g={{ ...G_X, id: "x" }} />;
const ShFacebook = (p) => <CircleMark {...p} g={{ ...G_FACEBOOK, id: "fb" }} />;

/* LinkedIn is delivered as a rounded square with the logo already knocked
   out of it, so the logo alone has to be recovered before it can be cut out
   of a circle: hide the square, show the square back minus its holes, and
   what is left masked off is the logo. */
const ShLinkedIn = ({ size = 22 }) => (
  <Svg48 size={size}>
    <mask id="limask" maskUnits="userSpaceOnUse" x="0" y="0" width="48" height="48">
      <circle cx="24" cy="24" r="24" fill="#fff" />
      <g transform="translate(9 9) scale(0.625)">
        <rect width="48" height="48" fill="#000" />
        <path d="__LI__" fill="#fff" />
      </g>
    </mask>
    <circle cx="24" cy="24" r="24" fill="currentColor" mask="url(#limask)" />
  </Svg48>
);

'''
block = (block.replace("__FB__", FB).replace("__TT__", TT).replace("__X__", X)
         .replace("__YTBOX__", YT_BOX).replace("__YTTRI__", YT_TRI).replace("__LI__", LI))

# Drop the hand-drawn share marks this replaces.
start = s.index("/* ---------------- Share marks ----------------")
end = s.index("/* Instagram is deliberately absent")
old_block = s[start:end]
assert "const ShX" in old_block and "const ShLinkedIn" in old_block
# keep the utility marks (mail, link, check) that the old block also defined
keep = old_block[old_block.index("/* Not brands, and no supplied mark"):]
s = s[:start] + block + keep + s[end:]

io.open(p, 'w', encoding='utf-8').write(s)
print('brand glyphs in; share marks rebuilt from the files')
