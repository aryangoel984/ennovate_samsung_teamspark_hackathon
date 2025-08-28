import pyshark
import pandas as pd

# Load labels
labels = pd.read_csv("dataset.csv")

# Read PCAP
cap = pyshark.FileCapture("PCAPdroid_28_Aug_21_02_36.pcap")

flow_data = []

for pkt in cap:
    try:
        ts = float(pkt.sniff_timestamp)  # epoch timestamp
        src = pkt.ip.src
        dst = pkt.ip.dst
        proto = pkt.highest_layer
        length = int(pkt.length)

        # Match with dataset.csv time window
        label_row = labels[
            (labels['start_epoch'] <= ts) & (labels['end_epoch'] >= ts)
        ]
        if not label_row.empty:
            label = label_row.iloc[0]['action']
        else:
            label = "unlabeled"

        flow_data.append({
            "timestamp": ts,
            "src": src,
            "dst": dst,
            "proto": proto,
            "length": length,
            "label": label
        })
    except Exception as e:
        continue

cap.close()

# Save as feature dataset
df = pd.DataFrame(flow_data)
df.to_csv("flows_with_labels.csv", index=False)
print("✅ Correlated dataset saved as flows_with_labels.csv")
