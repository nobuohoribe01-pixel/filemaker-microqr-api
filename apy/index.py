from flask import Flask, request, abort, Response
from io import BytesIO
import segno

app = Flask(__name__)

@app.get("/microqr")
def microqr():
    data = request.args.get("data", "")
    if not data:
        abort(400, "data required")

    ver = (request.args.get("ver","M3")).upper()
    if ver not in ("M1","M2","M3","M4"):
        abort(400, "ver must be M1|M2|M3|M4")

    ecc = (request.args.get("ecc","M")).upper()
    if ecc not in ("L","M","Q"):
        abort(400, "ecc must be L|M|Q")

    def clamp(v, lo, hi): return max(lo, min(hi, v))
    scale = clamp(int(request.args.get("scale", 5)), 1, 64)
    quiet = clamp(int(request.args.get("quiet", 2)), 0, 16)
    dpi   = clamp(int(request.args.get("dpi", 600)), 72, 1200)
    invert = request.args.get("invert","0") in ("1","true","True")

    try:
        qr = segno.make(data, micro=True, version=ver, error=ecc)
    except Exception as e:
        abort(400, f"cannot encode as MicroQR {ver}/{ecc}: {e}")

    buf = BytesIO()
    qr.save(buf, kind="png", scale=scale, border=quiet, dpi=dpi,
            dark=("white" if invert else "black"),
            light=("black" if invert else "white"))
    png = buf.getvalue()
    # 余計なヘッダを付けない（FileMakerが直接画像として扱えるように）
    return Response(png, mimetype="image/png", headers={"Cache-Control":"no-store"})
