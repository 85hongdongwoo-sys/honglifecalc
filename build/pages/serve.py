# local preview server: overlay/ first, then $HL_ORIG
import http.server, os, sys
O=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','overlay'); B=os.environ.get('HL_ORIG','/tmp/hl_orig')
class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, p):
        p=p.split('?')[0].split('#')[0]
        for r in (O,B):
            f=os.path.join(r,p.lstrip('/'))
            if os.path.isdir(f): f=os.path.join(f,'index.html')
            if os.path.exists(f): return f
        return os.path.join(B,p.lstrip('/'))
    def log_message(self,*a): pass
http.server.ThreadingHTTPServer(('127.0.0.1',int(sys.argv[1]) if len(sys.argv)>1 else 8765),H).serve_forever()
