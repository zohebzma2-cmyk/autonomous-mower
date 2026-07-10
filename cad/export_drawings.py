#!/usr/bin/env python3
"""Generate dimensioned drawing-sheet PDFs for the flat/laser-cut parts.
Reads the OpenSCAD 2D outline SVGs (run export_dxf.sh first, which also leaves
drawings/*.svg) + stl/MANIFEST.csv, and writes drawings/<part>_drawing.pdf.
Deps: pip install cairosvg.  Pair each PDF with its dxf/<part>.dxf for the shop."""
import re, csv, os, cairosvg
names={'PRINT_estop_face':'E-stop face','PRINT_relay_lid':'Relay lid','PRINT_badge':'Nameplate badge','PRINT_upper_shelf':'Upper shelf','PRINT_lapbar_yoke_top':'Lap-bar yoke (upper)','PRINT_lapbar_yoke_bottom':'Lap-bar yoke (lower)','PRINT_lidar_top_plate':'LiDAR top plate','PRINT_gps_top_plate':'GPS antenna plate'}
th={'PRINT_estop_face':3,'PRINT_relay_lid':6,'PRINT_badge':3,'PRINT_upper_shelf':10,'PRINT_lapbar_yoke_top':10,'PRINT_lapbar_yoke_bottom':10,'PRINT_lidar_top_plate':14,'PRINT_gps_top_plate':24}
HERE=os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
mani={r['part']:r for r in csv.DictReader(open('stl/MANIFEST.csv'))}
def sheet(part):
    svg=open(f'drawings/{part}.svg').read()
    vx,vy,vw,vh=map(float,re.search(r'viewBox="([\-0-9. ]+)"',svg).group(1).split())
    path=re.sub(r'\s(style|fill|stroke[^=]*)="[^"]*"','',re.search(r'(<path[^>]*d="[^"]*"[^>]*/?>)',svg,re.S).group(1))
    W,H=1123,794; dax,day,daw,dah=70,70,620,600
    sc=min(daw/vw,dah/vh)*0.72; cx,cy=dax+daw/2,day+dah/2; bw,bh=vw*sc,vh*sc
    px,py=float(mani[part]['bbox_x']),float(mani[part]['bbox_y'])
    dH=lambda y,a,b,v:f'<line x1="{a}" y1="{y}" x2="{b}" y2="{y}" stroke="#c0392b" stroke-width="1"/><path d="M{a},{y} l6,-3 l0,6 z" fill="#c0392b"/><path d="M{b},{y} l-6,-3 l0,6 z" fill="#c0392b"/><text x="{(a+b)/2}" y="{y-6}" font-family="monospace" font-size="15" fill="#c0392b" text-anchor="middle">{v:.1f} mm</text>'
    dV=lambda x,a,b,v:f'<line x1="{x}" y1="{a}" x2="{x}" y2="{b}" stroke="#c0392b" stroke-width="1"/><path d="M{x},{a} l-3,6 l6,0 z" fill="#c0392b"/><path d="M{x},{b} l-3,-6 l6,0 z" fill="#c0392b"/><text x="{x-8}" y="{(a+b)/2}" font-family="monospace" font-size="15" fill="#c0392b" text-anchor="middle" transform="rotate(-90 {x-8} {(a+b)/2})">{v:.1f} mm</text>'
    tbx,tby,tbw,tbh=713,548,340,176
    tb='\n'.join(f'<line x1="{tbx}" y1="{tby+26+i*26-13}" x2="{tbx+tbw}" y2="{tby+26+i*26-13}" stroke="#999" stroke-width="0.6"/><text x="{tbx+10}" y="{tby+26+i*26}" font-family="monospace" font-size="12" fill="#555">{k}</text><text x="{tbx+130}" y="{tby+26+i*26}" font-family="monospace" font-size="12.5" font-weight="bold" fill="#111">{v}</text>' for i,(k,v) in enumerate([('PART',names[part]),('MATERIAL','6061-T6 alum'),('THICKNESS',f'{th[part]} mm'),('PROCESS','laser cut'),('FINISH','anodize II'),('TOLERANCE','ISO 2768-m'),('QTY','1'),('FILE',f'dxf/{part}.dxf')]))
    out=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#fff"/><rect x="24" y="24" width="{W-48}" height="{H-48}" fill="none" stroke="#333" stroke-width="1.5"/><text x="46" y="52" font-family="monospace" font-size="18" font-weight="bold" fill="#111">{names[part]}</text><text x="46" y="70" font-family="monospace" font-size="11" fill="#777">Autonomous ZT X 52 retrofit — flat part, laser cut · github.com/zohebzma2-cmyk/autonomous-mower</text><g transform="translate({cx},{cy}) scale({sc},{-sc}) translate({-(vx+vw/2)},{-(vy+vh/2)})"><g fill="#dfe6ee" stroke="#1a1a1a" stroke-width="{0.6/sc}">{path}</g></g>{dH(cy+bh/2+34,cx-bw/2,cx+bw/2,px)}{dV(cx-bw/2-34,cy-bh/2,cy+bh/2,py)}<rect x="{tbx}" y="{tby-24}" width="{tbw}" height="{tbh+24}" fill="#fafafa" stroke="#333" stroke-width="1.2"/><text x="{tbx+10}" y="{tby-8}" font-family="monospace" font-size="11" font-weight="bold" fill="#c0392b">FABRICATION SPEC</text>{tb}</svg>'''
    open(f'drawings/{part}_drawing.svg','w').write(out)
    cairosvg.svg2pdf(bytestring=out.encode(),write_to=f'drawings/{part}_drawing.pdf')
if __name__=='__main__':
    for p in names: sheet(p); print('  drawings/'+p+'_drawing.pdf')
