#!/usr/bin/env python3
"""
calibrate_ui.py
Usage:
  ./calibrate_ui.py ui.xml "Reels" "resource-id-or-empty"
Will search for nodes by text (first arg) or resource-id (second arg if provided).
Prints JSON with center coordinates for found nodes and writes coords.json.
"""

import sys, xml.etree.ElementTree as ET, json, re, pathlib

def parse_bounds(b):
    # b looks like "[x1,y1][x2,y2]"
    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", b)
    if not m:
        return None
    x1,y1,x2,y2 = map(int, m.groups())
    cx = (x1 + x2)//2
    cy = (y1 + y2)//2
    return {'x1':x1,'y1':y1,'x2':x2,'y2':y2,'cx':cx,'cy':cy}

def find_nodes(tree, text=None, resid=None):
    nodes = []
    for n in tree.iter():
        t = n.attrib.get('text','').strip()
        r = n.attrib.get('resource-id','').strip()
        b = n.attrib.get('bounds','').strip()
        if b=='':
            # some dumps use 'bounds' attribute name or not - try 'bounds' already used.
            b = n.attrib.get('bounds','').strip()
        if text and t.lower()==text.lower() and b:
            nodes.append((n, b))
        elif resid and r==resid and b:
            nodes.append((n,b))
    return nodes

def main():
    if len(sys.argv) < 2:
        print("Usage: calibrate_ui.py ui.xml [text_to_find] [resource_id_to_find]")
        sys.exit(1)
    ui_path = pathlib.Path(sys.argv[1])
    text_arg = sys.argv[2] if len(sys.argv)>2 else ''
    resid_arg = sys.argv[3] if len(sys.argv)>3 else ''
    tree = ET.parse(str(ui_path))
    root = tree.getroot()

    coords = {}
    if text_arg:
        found = find_nodes(root, text=text_arg)
        if found:
            # use first match
            b = found[0][1]
            coords[text_arg] = parse_bounds(b)
    if resid_arg:
        found = find_nodes(root, resid=resid_arg)
        if found:
            b = found[0][1]
            coords[resid_arg] = parse_bounds(b)

    # Also try to find common bottom nav icons heuristically:
    # Find any node near bottom with bounds center y > 0.85*height
    # Determine screen height from root bounds if present
    root_bounds = root.attrib.get('bounds','')
    screen_h = None
    if root_bounds:
        pb = parse_bounds(root_bounds)
        screen_h = pb['y2']
    # fallback: look for nodes with package attribute and high bounds
    bottom_nodes = []
    for n in root.iter():
        b = n.attrib.get('bounds','')
        if not b: continue
        pb = parse_bounds(b)
        if pb and screen_h and pb['cy'] > 0.80*screen_h:
            bottom_nodes.append((n, pb))
    if bottom_nodes and 'bottom_nav' not in coords:
        # pick median x center as center of bottom nav area
        xs = [bn[1]['cx'] for bn in bottom_nodes]
        ys = [bn[1]['cy'] for bn in bottom_nodes]
        coords['bottom_nav_estimate'] = {'cx': int(sum(xs)/len(xs)), 'cy': int(sum(ys)/len(ys))}
    # Write out coords.json
    out = {"found": coords, "screen_height": screen_h}
    with open("coords.json","w") as f:
        json.dump(out, f, indent=2)
    print("Wrote coords.json. Contents:")
    print(json.dumps(out, indent=2))

if __name__=='__main__':
    main()
