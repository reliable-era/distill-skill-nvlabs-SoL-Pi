"""Runtime-only dedicated token;redaction BEFORE any persistent stream write."""
import contextlib,os,pathlib,stat,tempfile
TOKEN_FILE=pathlib.Path.home()/'.config/solpi-g6/claude-oauth-token'
def read_token(path=TOKEN_FILE):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or stat.S_IMODE(s.st_mode)!=0o600 or s.st_uid!=os.getuid():
            raise RuntimeError('Dedicated token must be an owned regular mode600 file')
        token=os.read(fd,16384).strip()
    finally: os.close(fd)
    if not token.startswith(b'sk-ant-oat') or len(token)<20 or any(chr(c).isspace() for c in token): raise RuntimeError('Dedicated token format invalid')
    return token
@contextlib.contextmanager
def env_file(token):
    with tempfile.TemporaryDirectory(prefix='solpi-g6-env-',dir='/dev/shm') as directory:
        p=pathlib.Path(directory)/'runtime.env';fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'wb') as out: out.write(b'CLAUDE_CODE_OAUTH_TOKEN='+token+b'\n')
        yield str(p)
def filtered_copy(source,destination,token):
    """Same-length replacement also preserves ordinary tar payload framing."""
    pending=b'';count=0;size=len(token)
    assert size
    while True:
        chunk=source.read(65536)
        if not chunk: break
        pending+=chunk;count+=pending.count(token);pending=pending.replace(token,b'X'*size)
        end=max(0,len(pending)-size+1);destination.write(pending[:end]);pending=pending[end:]
    count+=pending.count(token);destination.write(pending.replace(token,b'X'*size))
    return count
