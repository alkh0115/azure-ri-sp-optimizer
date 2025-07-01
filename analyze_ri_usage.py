import json

# Load usage data
with open("ri_usage_report.json", "r") as f:
    data = json.load(f)

# Group usage by Reservation ID
usage_summary = {}
for entry in data:
    rid = entry["reservationId"]
    usage_summary.setdefault(rid, []).append(entry["cost"])

# Analyze utilization
recommendations = []
threshold = 0.5  # 50%

for rid, costs in usage_summary.items():
    total_usage = sum(costs)
    max_possible = max(costs) * len(costs)
    utilization = total_usage / max_possible if max_possible > 0 else 0

    if utilization < threshold:
        recommendations.append({
            "reservationId": rid,
            "utilizationPercent": round(utilization * 100, 2),
            "action": "Consider modifying or exchanging this RI to better match workload."
        })

# Save to JSON
output_file = "ri_recommendations.json"
with open(output_file, "w") as f:
    json.dump(recommendations, f, indent=2)

print(f"\n Optimization recommendations saved to {output_file}")
