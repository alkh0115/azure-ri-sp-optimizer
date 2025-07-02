import json

def analyze_ri_data():
    input_file = "ri_usage_report.json"
    output_file = "ri_recommendations.json"

    try:
        with open(input_file, "r") as f:
            data = json.load(f)

        # Dummy logic: Recommend consolidating if cost < threshold
        recommendations = []
        for item in data:
            if item["cost"] < 10:
                recommendations.append({
                    "instanceName": item["instanceName"],
                    "recommendation": "Consider consolidating or resizing",
                    "cost": item["cost"],
                    "date": item["usageDate"]
                })

        with open(output_file, "w") as f:
            json.dump(recommendations, f, indent=2)

        print(f" Optimization recommendations saved to {output_file}")

    except Exception as e:
        print(f" Error in analysis: {e}")

# Optional local test
if __name__ == "__main__":
    analyze_ri_data()
