from flask import Flask, request, abort, Response
from io import BytesIO
import segno

app = Flask(__name__)

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def get_int(name, default, lo=None, hi=None):
    raw = request.args.get(name, None)
    if raw is None or raw == "":
        v = default
    else:
        try:
            v = int(raw)
        except Exception:
            v = default
    if lo is not None and hi is not None:
        v = clamp(v, lo, hi)
    return v

def get_choice(name, default, choices, transform=str.upper):
    raw = request.args.get(name, None)
    if raw is None or raw == "":
        return default
    val = transform(raw) if transform else raw
    return val if val in choices else default

def build_png(data, ver, ecc, scale, quiet, dpi, invert):
    qr = segno.make(data, micro=True, version=ver, error=ecc)
    buf = BytesIO()
    qr.save(
        buf, kind="png",
        scale=scale, border=quiet, dpi=dpi,
        dark=("white" if invert else "black"),
        light=("black" if invert else "white"),
    )
    return buf.getvalue()

def handle():
    data = request.args.get("data", "")
    if not data:
        abort(400, "data required")

    ver    = get_choice("ver",  "M3", {"M1","M2","M3","M4"})
    ecc    = get_choice("ecc",  "M",  {"L","M","Q"})
    scale  = get_int("scale",  8, 1, 64)
    quiet  = get_int("quiet",  2, 0, 16)
    dpi    = get_int("dpi",   600, 72, 1200)
    invert = request.args.get("invert","0").lower() in ("1","true","yes")

    try:
        png = build_png(data, ver, ecc, scale, quiet, dpi, invert)
    except Exception as e:
        abort(400, f"cannot encode as MicroQR {ver}/{ecc}: {e}")

    return Response(png, mimetype="image/png", headers={"Cache-Control":"no-store"})

@app.get("/")
@app.get("/microqr")
def microqr():
    return handle()
