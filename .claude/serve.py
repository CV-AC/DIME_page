"""Static file server with HTTP Range support (for local video preview)."""
import os, sys, socket
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

class RangeHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path) or "Range" not in self.headers:
            return super().send_head()
        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found"); return None
        size = os.fstat(f.fileno()).st_size
        rng = self.headers["Range"].replace("bytes=", "").split("-")
        start = int(rng[0]) if rng[0] else 0
        end = int(rng[1]) if len(rng) > 1 and rng[1] else size - 1
        end = min(end, size - 1)
        if start > end:
            self.send_error(416, "Range not satisfiable"); f.close(); return None
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        f.seek(start); self._range_left = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        left = getattr(self, "_range_left", None)
        if left is None:
            return super().copyfile(source, outputfile)
        try:
            while left > 0:
                chunk = source.read(min(65536, left))
                if not chunk: break
                outputfile.write(chunk); left -= len(chunk)
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass  # client closed the range request early; normal for video

    def end_headers(self):
        if self.command == "GET" and "Range" not in self.headers:
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

class DualStackServer(ThreadingHTTPServer):
    address_family = socket.AF_INET6
    def server_bind(self):
        try:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except OSError:
            pass
        super().server_bind()

if __name__ == "__main__":
    port = int(sys.argv[1]); os.chdir(sys.argv[2])
    DualStackServer(("::", port), RangeHandler).serve_forever()
