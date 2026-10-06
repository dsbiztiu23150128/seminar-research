"""Inline local display assets for browser-based GitHub upload; preserve page links."""
from pathlib import Path
import re,base64,mimetypes,shutil
root=Path(__file__).resolve().parent
src=root/'docs'; out=root/'publish';out.mkdir(exist_ok=True)
def uri(p):
 return 'data:'+(mimetypes.guess_type(p.name)[0] or 'application/octet-stream')+';base64,'+base64.b64encode(p.read_bytes()).decode()
def css(p):
 text=p.read_text()
 def sub(m):
  rel=m.group(1).strip(' "\''); target=p.parent/rel.split('?')[0].split('#')[0]
  return 'url("'+uri(target)+'")' if target.is_file() else m.group(0)
 return re.sub(r'url\(([^)]+)\)',sub,text)
for p in src.glob('*.html'):
 s=p.read_text()
 def script(m):
  target=src/m.group(2)
  return '<script'+m.group(1)+m.group(3)+'>'+target.read_text().replace('</script','<\\/script')+'</script>' if target.is_file() else m.group(0)
 s=re.sub(r'<script([^>]*?) src="([^"]+)"([^>]*)></script>',script,s)
 def style(m):
  target=src/m.group(1)
  return '<style>'+css(target)+'</style>' if target.is_file() else m.group(0)
 s=re.sub(r'<link[^>]*href="([^"]+)"[^>]*rel="stylesheet"[^>]*>',style,s)
 s=re.sub(r'src="([^"]+)"',lambda m:'src="'+uri(src/m.group(1))+'"' if (src/m.group(1)).is_file() else m.group(0),s)
 (out/p.name).write_text(s)
shutil.copy(src/'search.json',out/'search.json')
print([(p.name,p.stat().st_size) for p in out.iterdir()])
