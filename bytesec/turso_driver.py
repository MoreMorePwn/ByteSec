"""
Pure-Python DBAPI 2.0 driver for Turso (libSQL over HTTP).
Zero native dependencies — uses only urllib from stdlib.
Compatible with SQLAlchemy via the creator= parameter.
"""
import json
import urllib.request
import urllib.error

apilevel = "2.0"
threadsafety = 1
paramstyle = "qmark"

_type_string = str
_type_bytes = bytes
_type_int = int
_type_float = float
_type_none = type(None)


def _type_val(val):
    if val is None:
        return {"type": "null"}
    if isinstance(val, _type_int):
        return {"type": "integer", "value": str(val)}
    if isinstance(val, _type_float):
        return {"type": "float", "value": str(val)}
    if isinstance(val, _type_bytes):
        return {"type": "blob", "value": val.decode("latin-1")}
    # treat everything else as text
    return {"type": "text", "value": str(val)}


def _parse_val(col):
    if col is None or col.get("type") == "null":
        return None
    t = col.get("type")
    v = col.get("value")
    if t == "integer":
        return int(v)
    if t == "float":
        return float(v)
    if t == "blob":
        return bytes(v, "latin-1")
    return str(v)  # text


class TursoCursor:
    def __init__(self, conn):
        self.connection = conn
        self.description = None
        self.rowcount = -1
        self.arraysize = 1
        self._results = []
        self._rowindex = 0
        self.lastrowid = None

    # ── helpers ──

    def _call(self, sql, params=None):
        args = []
        if params:
            for p in params:
                args.append(_type_val(p))

        body = json.dumps({
            "requests": [
                {"type": "execute", "stmt": {"sql": sql, "args": args}},
                {"type": "close"},
            ]
        }).encode()

        req = urllib.request.Request(
            self.connection._url,
            data=body,
            headers={
                "Authorization": f"Bearer {self.connection._token}",
                "Content-Type": "application/json",
            },
        )
        return urllib.request.urlopen(req, timeout=30)

    def _parse_response(self, resp_data):
        rows = resp_data.get("rows", [])
        self.description = [
            (c["name"], c.get("decltype"), None, None, None, None, None)
            for c in resp_data.get("cols", [])
        ] or None
        self._results = [tuple(_parse_val(r[c]) for c in range(len(r))) for r in rows]
        self._rowindex = 0
        self.rowcount = resp_data.get("affected_row_count", -1)
        lrid = resp_data.get("last_insert_rowid")
        self.lastrowid = int(lrid) if lrid is not None else None

    def _execute_pipeline(self, sql, params=None):
        resp = self._call(sql, params)
        data = json.loads(resp.read())
        results = data.get("results", [])
        if not results:
            return

        first = results[0]
        if first.get("type") != "ok":
            err = first.get("error", first.get("response", first))
            raise RuntimeError(f"Turso error: {err}")

        r = first.get("response", {})
        if r.get("type") == "execute":
            self._parse_response(r.get("result", {}))

    # ── DBAPI 2.0 interface ──

    def execute(self, sql, params=None):
        if params is not None:
            params = list(params)
        self._execute_pipeline(sql, params)
        return self

    def executemany(self, sql, seq_of_params):
        for p in seq_of_params:
            self.execute(sql, p)
        return self

    def fetchone(self):
        if self._rowindex >= len(self._results):
            return None
        row = self._results[self._rowindex]
        self._rowindex += 1
        return row

    def fetchmany(self, size=None):
        if size is None:
            size = self.arraysize
        remaining = len(self._results) - self._rowindex
        actual = min(size, remaining)
        if actual <= 0:
            return []
        result = self._results[self._rowindex:self._rowindex + actual]
        self._rowindex += actual
        return result

    def fetchall(self):
        remaining = self._results[self._rowindex:]
        self._rowindex = len(self._results)
        return remaining

    def setinputsizes(self, *args):
        pass

    def setoutputsize(self, *args):
        pass

    def close(self):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        row = self.fetchone()
        if row is None:
            raise StopIteration
        return row


class TursoConnection:
    def __init__(self, url, auth_token):
        # Strip trailing /v2/pipeline if already present
        base = url.rstrip("/")
        if base.endswith("/v2/pipeline"):
            base = base[: -len("/v2/pipeline")]
        self._url = base + "/v2/pipeline"
        self._token = auth_token

    def cursor(self):
        return TursoCursor(self)

    def commit(self):
        pass  # HTTP mode auto-commits

    def create_function(self, name, num_params, func, deterministic=False):
        pass  # Turso HTTP driver doesn't support custom SQL functions

    def rollback(self):
        pass

    def execute(self, sql, params=None):
        return self.cursor().execute(sql, params)

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass


def connect(url, auth_token):
    """Create a Turso connection. Accepts raw libsql:// or https:// URLs."""
    return TursoConnection(url, auth_token)
