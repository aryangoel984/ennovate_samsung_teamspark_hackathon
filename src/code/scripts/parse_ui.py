#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET

def classify_ui(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    found_video = False
    found_image = False
    found_ad = False

    for node in root.iter("node"):
        rid = node.attrib.get("resource-id", "").lower()
        clazz = node.attrib.get("class", "").lower()
        text = node.attrib.get("text", "").lower()

        # Heuristics (adjust based on Instagram UI)
        if "video" in rid or "reel" in rid or "videocontainer" in rid or "videoplayer" in clazz:
            found_video = True
        elif "image" in rid or "imageview" in clazz:
            found_image = True
        if "sponsored" in text or "ad" in rid:
            found_ad = True

    if found_video:
        return "feed_video"
    elif found_ad:
        return "feed_ad"
    elif found_image:
        return "feed_image"
    else:
        return "unknown"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: parse_ui.py ui.xml")
        sys.exit(1)
    action = classify_ui(sys.argv[1])
    print(action)
