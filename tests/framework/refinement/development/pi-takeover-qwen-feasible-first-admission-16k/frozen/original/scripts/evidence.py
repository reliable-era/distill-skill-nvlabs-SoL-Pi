#!/usr/bin/env python3
"""Archive exact UTF-8 logs, recall pages, and verify evidence receipts offline."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

RECORD_SCHEMA = "efficient-coding-log/1"
RECEIPT_SCHEMA = "efficient-coding-receipt/1"
KINDS = {"fatal", "failure", "warning", "target", "summary"}
HASH = re.compile(r"[a-f0-9]{64}\Z")
MAX_SOURCE_BYTES = 64 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def regular_bytes(path):
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), "rb") as stream:
        import stat
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("Expected a regular file")
        if info.st_size > MAX_SOURCE_BYTES:
            raise ValueError("File exceeds the 64 MiB helper limit")
        data = stream.read(MAX_SOURCE_BYTES + 1)
    if len(data) > MAX_SOURCE_BYTES:
        raise ValueError("File exceeds the 64 MiB helper limit")
    return data


def write_once(path, data):
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    except FileExistsError:
        if regular_bytes(path) != data:
            raise ValueError("Existing archive object differs; refusing overwrite")
        return
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)


def excerpt(text, reverse=False, budget=512):
    selected = []
    used = 0
    lines = text.splitlines(keepends=True)
    for line in reversed(lines) if reverse else lines:
        size = len(line.encode("utf-8"))
        if used + size > budget:
            break
        selected.append(line)
        used += size
    if reverse:
        selected.reverse()
    return "".join(selected)


def store(args):
    data = regular_bytes(Path(args.input).absolute())
    text = data.decode("utf-8")
    root = Path(args.store_dir).absolute()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Archive directory must be a regular directory")
    source_hash = digest(data)
    archive = root / (source_hash + ".log")
    write_once(archive, data)
    record = {"schema": RECORD_SCHEMA, "source_sha256": source_hash,
              "source_bytes": len(data), "source_lines": len(text.splitlines()),
              "archive_path": str(archive), "exit_code": args.exit_code,
              "command": args.command}
    record_data = encode(record)
    record_path = root / ("run-" + digest(record_data)[:24] + ".json")
    write_once(record_path, record_data)
    head, tail = excerpt(text), excerpt(text, reverse=True)
    return {"record_path": str(record_path), **record,
            "status": "success" if args.exit_code == 0 else "failure",
            "head": head, "tail": tail,
            "omitted_content": len(head.encode("utf-8")) + len(tail.encode("utf-8")) < len(data),
            "note": "Exit code was supplied by caller; original evidence remains available."}


def load_record(path):
    record = json.loads(regular_bytes(Path(path).absolute()))
    expected = {"schema", "source_sha256", "source_bytes", "source_lines",
                "archive_path", "exit_code", "command"}
    if not isinstance(record, dict) or set(record) != expected:
        raise ValueError("Invalid log record fields")
    if record["schema"] != RECORD_SCHEMA or not isinstance(record["source_sha256"], str):
        raise ValueError("Invalid log record schema/hash")
    if not HASH.fullmatch(record["source_sha256"]):
        raise ValueError("Invalid source hash")
    for field in ("exit_code", "source_bytes", "source_lines"):
        if type(record[field]) is not int:
            raise ValueError("Record counts/status must be integers")
    if record["source_bytes"] < 0 or record["source_lines"] < 0:
        raise ValueError("Negative source size")
    if not isinstance(record["archive_path"], str) or not Path(record["archive_path"]).is_absolute():
        raise ValueError("Archive path must be absolute")
    if not isinstance(record["command"], str):
        raise ValueError("Invalid command")
    data = regular_bytes(record["archive_path"])
    text = data.decode("utf-8")
    if (digest(data) != record["source_sha256"] or len(data) != record["source_bytes"]
            or len(text.splitlines()) != record["source_lines"]):
        raise ValueError("Archive integrity check failed")
    return record, data


def recall(args):
    record, data = load_record(args.record)
    start = args.offset
    if not 0 <= start <= len(data):
        raise ValueError("Offset outside archive")
    if args.max_bytes < 1 or args.max_bytes > 16 * 1024:
        raise ValueError("max-bytes must be between 1 and 16384")
    if args.max_lines < 1 or args.max_lines > 400:
        raise ValueError("max-lines must be between 1 and 400")
    if start < len(data) and data[start] & 0xC0 == 0x80:
        raise ValueError("Offset is inside a UTF-8 character; use returned next_offset")
    end = min(len(data), start + args.max_bytes)
    while end > start and end < len(data) and data[end] & 0xC0 == 0x80:
        end -= 1
    if end == start and start < len(data):
        raise ValueError("Increase max-bytes to include the next UTF-8 character")
    newline_count = 0
    for index in range(start, end):
        if data[index] == 10:
            newline_count += 1
            if newline_count == args.max_lines:
                end = index + 1
                break
    chunk = data[start:end]
    return {"archive_path": record["archive_path"], "offset": start,
            "next_offset": end, "eof": end == len(data), "chunk_bytes": len(chunk),
            "text": chunk.decode("utf-8")}


def verify(args):
    record, data = load_record(args.record)
    receipt = json.loads(regular_bytes(Path(args.receipt).absolute()))
    fields = {"schema", "source_sha256", "status", "uncertain", "evidence"}
    if not isinstance(receipt, dict) or set(receipt) != fields:
        raise ValueError("Invalid receipt fields")
    status = "success" if record["exit_code"] == 0 else "failure"
    if (receipt["schema"] != RECEIPT_SCHEMA
            or receipt["source_sha256"] != record["source_sha256"]
            or receipt["status"] != status or type(receipt["uncertain"]) is not bool):
        raise ValueError("Receipt schema, hash, status, or uncertainty mismatch")
    evidence = receipt["evidence"]
    if not isinstance(evidence, list) or not 1 <= len(evidence) <= 12:
        raise ValueError("Receipt requires 1 to 12 evidence items")
    for item in evidence:
        if not isinstance(item, dict) or set(item) != {"kind", "quote"}:
            raise ValueError("Invalid evidence fields")
        if not isinstance(item["kind"], str) or item["kind"] not in KINDS:
            raise ValueError("Invalid evidence kind")
        quote = item["quote"]
        if not isinstance(quote, str) or not 1 <= len(quote) <= 600:
            raise ValueError("Quote must contain 1 to 600 characters")
        if quote.encode("utf-8") not in data:
            raise ValueError("Unverifiable quote")
    if status == "failure" and not any(item["kind"] in {"fatal", "failure"} for item in evidence):
        raise ValueError("Failing output requires fatal/failure evidence")
    verified = {**receipt, "archive_path": record["archive_path"],
                "source_bytes": len(data), "exit_code": record["exit_code"],
                "omission_completeness": "not established"}
    verified_bytes = len(encode(verified))
    if verified_bytes >= len(data):
        raise ValueError("Verified receipt is not smaller than original; read original")
    return {"ok": True, "receipt_bytes": verified_bytes, "receipt": verified}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    p = sub.add_parser("store", help="Archive existing log; requires observed exit code")
    p.add_argument("--input", required=True)
    p.add_argument("--store-dir", required=True)
    p.add_argument("--exit-code", type=int, required=True)
    p.add_argument("--command", default="")
    p = sub.add_parser("recall", help="Return an exact bounded archive page")
    p.add_argument("--record", required=True)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--max-bytes", type=int, default=15872)
    p.add_argument("--max-lines", type=int, default=398)
    p = sub.add_parser("verify", help="Check receipt provenance and recorded status")
    p.add_argument("--record", required=True)
    p.add_argument("--receipt", required=True)
    args = parser.parse_args()
    try:
        value = {"store": store, "recall": recall, "verify": verify}[args.operation](args)
    except (OSError, ValueError, UnicodeError, TypeError, OverflowError) as error:
        print(json.dumps({"ok": False, "error": str(error)}), file=sys.stderr)
        return 1
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
