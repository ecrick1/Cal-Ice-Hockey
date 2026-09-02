# -*- coding: utf-8 -*-
"""LinkedIn as a bare glyph, and marks that are the size they are asked for.

Two faults, one of them arithmetic.

The header renders an icon at seventeen pixels. Each mark is drawn in a
forty-eight box with the glyph fitted to a height of twenty-four, so what
reached the screen was seventeen times twenty-four over forty-eight - eight
and a half pixels, half the size of the drawn icons they replaced. Fitted to
the high thirties now, so a glyph nearly fills its box and arrives at the
size the header asked for.

And they were inconsistent because they were fitted to one height regardless
of shape. A tall narrow f and a wide rounded rectangle set to the same
height are not the same size to look at - the rectangle is twice the area.
Each gets a height that suits its proportions instead, the tall ones taller
and the wide one shorter, so the row reads level.

LinkedIn arrives as three bare paths with no container, like Facebook and
TikTok. It no longer has to be recovered from a knockout by masking a square
and subtracting its holes - the mark is the mark. Glyphs carry a list of
paths rather than one, because this is the first with more than one shape.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()

FB = ("M24.645 40.6953V70H11.1834V40.6953H0V28.8129H11.1834V24.4896C11.1834 8.43935 "
      "17.8883 0 32.0747 0C36.4238 0 37.5111 0.698965 39.8927 1.26849V13.0215C37.2263 "
      "12.5555 36.4756 12.2966 33.7056 12.2966C30.4179 12.2966 28.6575 13.2286 27.0525 "
      "15.0666C25.4475 16.9046 24.645 20.0888 24.645 24.645V28.8388H39.8927L35.8025 "
      "40.7212H24.645V40.6953Z")

TT = ("M44.5893 2.66285L42.9004 0H32.6802V23.9831L32.6454 47.4092C32.6628 47.5833 32.6802 "
      "47.7747 32.6802 47.9488C32.6802 53.814 27.9097 58.6002 22.0248 58.6002C16.1399 "
      "58.6002 11.3693 53.8314 11.3693 47.9488C11.3693 42.0835 16.1399 37.2974 22.0248 "
      "37.2974C23.2435 37.2974 24.4275 37.5236 25.5244 37.9065V26.2108C24.3927 26.0194 "
      "23.2261 25.915 22.0248 25.915C9.88939 25.9324 0 35.818 0 47.9662C0 60.1144 9.88939 "
      "70 22.0422 70C34.195 70 44.0844 60.1144 44.0844 47.9662V20.1019C48.4893 24.5052 "
      "54.1827 28.8041 60.4854 30.179V18.2223C53.643 15.1939 46.8353 6.24814 44.5893 2.66285Z")

YT_BOX = ("M74.5024 60H14.4975C6.46861 60 0 52.8994 0 44.1657V15.8343C0 7.06509 6.50112 0 "
          "14.4975 0H74.5024C82.5313 0 88.9999 7.10059 88.9999 15.8343V44.1657C89.0324 "
          "52.9349 82.5313 60 74.5024 60Z")
YT_TRI = "M60.2426 29.5562L35 15V44.1124L60.2426 29.5562Z"

LI1 = "M15.8066 23.0188H1.17969V69.663H15.8066V23.0188Z"
LI2 = ("M55.3732 22.0077C54.834 21.9403 54.2611 21.9066 53.6881 21.8729C45.4984 21.5359 "
       "40.8812 26.389 39.2635 28.4786C38.8254 29.0515 38.6231 29.3886 38.6231 "
       "29.3886V23.1536H24.6366V69.7978H38.6231H39.2635C39.2635 65.0458 39.2635 60.3274 "
       "39.2635 55.5754C39.2635 53.014 39.2635 50.4526 39.2635 47.8912C39.2635 44.7232 "
       "39.0276 41.3529 40.6116 38.4545C41.9597 36.0279 44.3862 34.8147 47.1161 "
       "34.8147C55.2047 34.8147 55.3732 42.1281 55.3732 42.8021C55.3732 42.8358 55.3732 "
       "42.8695 55.3732 42.8695V70H70.0001V39.5667C70.0001 29.1526 64.7088 23.0188 55.3732 "
       "22.0077Z")
LI3 = ("M8.49301 16.986C13.1836 16.986 16.9861 13.1836 16.9861 8.49303C16.9861 3.80246 "
       "13.1836 0 8.49301 0C3.80244 0 0 3.80246 0 8.49303C0 13.1836 3.80244 16.986 8.49301 "
       "16.986Z")

X = ("M36.6526 3.8078H43.3995L28.6594 20.6548L46 43.5797H32.4225L21.7881 29.6759L9.61989 "
     "43.5797H2.86886L18.6349 25.56L2 3.8078H15.9222L25.5348 16.5165L36.6526 3.8078ZM34.2846 "
     "39.5414H38.0232L13.8908 7.63406H9.87892L34.2846 39.5414Z")

block = '''/* ---------------- Brand marks ----------------
 *
 * The delivered artwork. Every file arrives in a box of its own, so `fit`
 * centres it in a common forty-eight square at a chosen height.
 *
 * The height is chosen per mark rather than shared, because a tall narrow f
 * and a wide rounded rectangle set to the same height are not the same size
 * to look at - the rectangle is twice the area. The tall ones are given more
 * height and the wide one less, so a row of them reads level.
 *
 * They nearly fill the box on purpose. The header draws these at seventeen
 * pixels, and a glyph occupying half its box would arrive at eight.
 */
const fit = (w, h, target) => {
  const k = target / h;
  return "translate(" + ((48 - w * k) / 2) + " " + ((48 - target) / 2) + ") scale(" + k + ")";
};

const G_FACEBOOK = { id: "fb", paths: ["__FB__"], t: fit(39.9, 70, 42) };
const G_TIKTOK = { id: "tt", paths: ["__TT__"], t: fit(60.5, 70, 42) };
const G_LINKEDIN = { id: "li", paths: ["__LI1__", "__LI2__", "__LI3__"], t: fit(70, 70, 38) };
/* X is drawn inset in a forty-eight box of its own rather than filling it,
   so it is scaled about its centre instead of being fitted from a corner. */
const G_X = { id: "x", paths: ["__X__"], t: "translate(24 24) scale(0.86) translate(-24 -24)" };

const Svg48 = ({ size, children, extra }) => (
  <svg viewBox="0 0 48 48" width={size} height={size} fill="none" aria-hidden="true"
    focusable="false" {...extra}>{children}</svg>
);

const Paths = ({ g, fill }) => (
  <g transform={g.t}>{g.paths.map((d, i) => <path key={i} d={d} fill={fill} />)}</g>
);

/* A glyph on its own in the current colour - what the header wants, where
   the icons sit on navy and the disc is the hover state. */
const Glyph = ({ g, size = 18 }) => (
  <Svg48 size={size}><Paths g={g} fill="currentColor" /></Svg48>
);

function BrFacebook(p) { return <Glyph {...p} g={G_FACEBOOK} />; }
function BrTikTok(p) { return <Glyph {...p} g={G_TIKTOK} />; }
function BrX(p) { return <Glyph {...p} g={G_X} />; }

/* YouTube is a rounded rectangle with the play triangle knocked out of it.
   Masked rather than painted white, so what shows through the triangle is
   the navy at rest and the gold on hover. Set shorter than the others
   because it is half again as wide as it is tall. */
function BrYouTube({ size = 18 }) {
  return (
    <Svg48 size={size}>
      <mask id="ytmask" maskUnits="userSpaceOnUse" x="0" y="0" width="48" height="48">
        <g transform={fit(89, 60, 30)}>
          <path d="__YTBOX__" fill="#fff" />
          <path d="__YTTRI__" fill="#000" />
        </g>
      </mask>
      <rect width="48" height="48" fill="currentColor" mask="url(#ytmask)" />
    </Svg48>
  );
}

/* The mark in a filled circle with the logo cut out of it - what a story's
   share row wants, on white. The glyph is set smaller here than in the
   header, because here it has a disc around it rather than open space. */
const CircleMark = ({ g, size = 22, inset = 0.62 }) => (
  <Svg48 size={size}>
    <mask id={"cm" + g.id} maskUnits="userSpaceOnUse" x="0" y="0" width="48" height="48">
      <circle cx="24" cy="24" r="24" fill="#fff" />
      <g transform={"translate(24 24) scale(" + inset + ") translate(-24 -24)"}>
        <Paths g={g} fill="#000" />
      </g>
    </mask>
    <circle cx="24" cy="24" r="24" fill="currentColor" mask={"url(#cm" + g.id + ")"} />
  </Svg48>
);

/* X is already scaled down inside its own glyph, so it needs less here. */
const ShX = (p) => <CircleMark {...p} g={G_X} inset={0.55} />;
const ShFacebook = (p) => <CircleMark {...p} g={G_FACEBOOK} />;
const ShLinkedIn = (p) => <CircleMark {...p} g={G_LINKEDIN} />;

'''
for k, v in [("__FB__", FB), ("__TT__", TT), ("__X__", X), ("__YTBOX__", YT_BOX),
             ("__YTTRI__", YT_TRI), ("__LI1__", LI1), ("__LI2__", LI2), ("__LI3__", LI3)]:
    assert k in block
    block = block.replace(k, v)

start = s.index("/* ---------------- Brand marks ----------------")
end = s.index("/* Not brands, and no supplied mark")
s = s[:start] + block + s[end:]

io.open(p, 'w', encoding='utf-8').write(s)
print('linkedin from the file; marks sized to look level')
