import io
p = "../reference/cal-ice-hockey-app.jsx"
lines = io.open(p, encoding="utf-8").read().split(chr(10))
B = chr(92)
target = "}).replace(/AM/"
hits = [i for i, l in enumerate(lines) if target in l]
assert len(hits) == 1, hits
i = hits[0]
lines[i] = "  }).replace(/" + B + "bAM" + B + "b/, " + chr(34) + "am" + chr(34) + ").replace(/" + B + "bPM" + B + "b/, " + chr(34) + "pm" + chr(34) + ");"
io.open(p, "w", encoding="utf-8").write(chr(10).join(lines))
print(lines[i])
