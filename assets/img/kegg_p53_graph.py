"""Draw KEGG pathway hsa04115 (p53 signalling) as a graph from its KGML data.
    curl -s https://rest.kegg.jp/get/hsa04115/kgml -o hsa04115.xml
    python3 kegg_p53_graph.py kegg_p53_graph.svg
Our own drawing of KEGG relation data (Kanehisa Laboratories), not the KEGG map image."""
import xml.etree.ElementTree as ET, networkx as nx, math, sys, html
r=ET.parse('hsa04115.xml').getroot()
ent={e.get('id'):e for e in r.findall('entry')}
def label(i):
    e=ent[i]
    if e.get('type')=='group': return '·'.join(label(c.get('id')) for c in e.findall('component'))
    g=e.find('graphics'); return (g.get('name') or e.get('name')).split(',')[0].strip('.').strip()
G=nx.DiGraph()
for x in r.findall('relation'):
    a,b=label(x.get('entry1')),label(x.get('entry2'))
    st=[s.get('name') for s in x.findall('subtype')]
    kind='inhibition' if 'inhibition' in st else 'activation' if 'activation' in st else 'expression' if 'expression' in st else 'other'
    if a!=b: G.add_edge(a,b,kind=kind)
U=G.to_undirected()
deg=sorted(U.degree, key=lambda t:-t[1])
print('nodes',G.number_of_nodes(),'edges',G.number_of_edges(),'top',deg[:8], 'components', nx.number_connected_components(U))
print('TP53 out',G.out_degree('TP53'),'in',G.in_degree('TP53'))
pos=nx.kamada_kawai_layout(U)   # deterministic
W,H,M=900,520,40
xs=[p[0] for p in pos.values()]; ys=[p[1] for p in pos.values()]
def X(v): return M+(v-min(xs))/(max(xs)-min(xs))*(W-2*M)
def Y(v): return M+(v-min(ys))/(max(ys)-min(ys))*(H-2*M)
COL={'activation':'#2e9e5b','inhibition':'#d0453f','expression':'#9aa3b2','other':'#9aa3b2'}
key={'TP53','MDM2','MDM4','ATM','ATR','CDKN1A','BAX','CDK4·CCND1','CDK2·CCNE1','CDK1·CCNB1','CASP9'}
out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H+34}" font-family="Helvetica, Arial, sans-serif">',
     '<rect width="100%" height="100%" fill="#fff"/>',
     '<defs>'+''.join(f'<marker id="m{k}" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for k,c in COL.items())+
     '<marker id="bar" viewBox="0 0 4 12" refX="4" refY="6" markerWidth="4" markerHeight="10" orient="auto"><rect width="3" height="12" fill="#d0453f"/></marker></defs>']
R=lambda n: 22 if n=='TP53' else 7 if n in key else 5
for a,b,d in G.edges(data=True):
    x1,y1,x2,y2=X(pos[a][0]),Y(pos[a][1]),X(pos[b][0]),Y(pos[b][1])
    L=math.hypot(x2-x1,y2-y1) or 1; ex,ey=x2-(x2-x1)/L*(R(b)+2), y2-(y2-y1)/L*(R(b)+2)
    sx,sy=x1+(x2-x1)/L*R(a), y1+(y2-y1)/L*R(a)
    mk='url(#bar)' if d['kind']=='inhibition' else f"url(#m{d['kind']})"
    w=2.2 if d['kind'] in('activation','inhibition') else 1.1
    out.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{COL[d["kind"]]}" stroke-width="{w}" marker-end="{mk}" opacity="0.85"/>')
for n in G.nodes:
    x,y=X(pos[n][0]),Y(pos[n][1]); r_=R(n)
    fill='#6b4fd8' if n=='TP53' else '#d6cff7' if n in key else '#e9ecf2'
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r_}" fill="{fill}" stroke="#5b6475" stroke-width="1"><title>{html.escape(n)}</title></circle>')
    if n=='TP53': out.append(f'<text x="{x:.1f}" y="{y+5:.1f}" text-anchor="middle" font-size="14" font-weight="700" fill="#fff">TP53</text>')
    elif n in key: out.append(f'<text x="{x+9:.1f}" y="{y+4:.1f}" font-size="13" font-weight="600" fill="#1d2433" stroke="#fff" stroke-width="3" paint-order="stroke">{html.escape(n)}</text>')
ly=H+16
out.append(f'<g font-size="13" fill="#1d2433"><line x1="40" y1="{ly}" x2="80" y2="{ly}" stroke="#2e9e5b" stroke-width="2.2" marker-end="url(#mactivation)"/><text x="88" y="{ly+4}">activation / phosphorylation</text>'
           f'<line x1="300" y1="{ly}" x2="340" y2="{ly}" stroke="#d0453f" stroke-width="2.2" marker-end="url(#bar)"/><text x="348" y="{ly+4}">inhibition</text>'
           f'<line x1="450" y1="{ly}" x2="490" y2="{ly}" stroke="#9aa3b2" stroke-width="1.1" marker-end="url(#mexpression)"/><text x="498" y="{ly+4}">expression (TP53 switches the gene on)</text></g>')
out.append('</svg>')
open(sys.argv[1],'w').write('\n'.join(out))
