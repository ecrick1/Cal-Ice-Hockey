import io
p = "../reference/cal-ice-hockey-app.jsx"
raw = io.open(p, "rb").read()
BS = bytes([8])
repl = bytes([92, 98])   # backslash, b
n = raw.count(BS)
raw = raw.replace(BS, repl)
io.open(p, "wb").write(raw)
print("replaced", n, "backspace bytes; remaining:", io.open(p, "rb").read().count(BS))
