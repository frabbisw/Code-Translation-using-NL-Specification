import json
import matplotlib.pyplot as plt

def generate_issues_chart(json_file='tags.json', output_file='tags.png'):
    # 1. Load Data
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_file} not found. Please ensure the file exists.")
        return

    # 2. Extract unique languages to determine grid size
    languages = set()
    for key in data.keys():
        if "_to_" in key:
            parts = key.split("_to_")
            if len(parts) == 2:
                languages.add(parts[0])
                languages.add(parts[1])
    
    lang_list = sorted(list(languages))
    n = len(lang_list)
    
    if n == 0:
        print("No valid 'Src_to_Tgt' keys found in JSON.")
        return

    # --- ADJUSTMENT 1: INCREASE FIGURE SIZE ---
    # Previous: figsize=(4 * n, 4 * n)
    # New: figsize=(6 * n, 6 * n) -> This makes the chart significantly larger in dimensions.
    fig, axes = plt.subplots(n, n, figsize=(6 * n, 6 * n), constrained_layout=True)
    
    # Increase title font size to match new scale
    # fig.suptitle('SonarQube Issues Distribution: Source (X-axis) vs Target (Y-axis)', fontsize=30, weight='bold')

    # 4. Iterate through the grid
    for i, target_lang in enumerate(lang_list):      # Row = Target
        for j, source_lang in enumerate(lang_list):  # Col = Source
            
            ax = axes[i, j] if n > 1 else axes
            key = f"{source_lang}_to_{target_lang}"
            
            # Label Axes (headers) - Increased font size
            if i == 0:
                ax.set_title(source_lang, fontsize=24, weight='bold', pad=20) 
            if j == 0:
                ax.set_ylabel(target_lang, fontsize=24, weight='bold', rotation=90, labelpad=20)

            if source_lang == target_lang:
                ax.text(0.5, 0.5, "N/A", ha='center', va='center', color='grey', fontsize=20)
                ax.axis('off')
            elif key in data:
                issues = data[key]
                labels = [item['topic'] for item in issues]
                counts = [item['count'] for item in issues]
                
                wedges, texts, autotexts = ax.pie(
                    counts, 
                    autopct='%1.0f%%',
                    startangle=90,
                    pctdistance=0.85,
                    # Increased font size for percentages inside pie
                    textprops={'fontsize': 20} 
                )
                
                # Legend - Increased font size
                ax.legend(
                    wedges, 
                    labels, 
                    title="Top Issues", 
                    loc="center left", 
                    bbox_to_anchor=(1, 0, 0.5, 1),
                    fontsize=13 # 'small' relative to the larger figure is readable
                )
                ax.set_aspect('equal')
            else:
                ax.text(0.5, 0.5, "No Data", ha='center', va='center', color='grey', fontsize=20)
                ax.axis('off')

    # Global axis labels - Increased font size
    fig.text(0.5, 0.02, 'Source Language', ha='center', fontsize=26, weight='bold')
    fig.text(0.02, 0.5, 'Target Language', va='center', rotation='vertical', fontsize=26, weight='bold')

    # --- ADJUSTMENT 2: INCREASE RESOLUTION (DPI) ---
    # dpi=300 is standard high-resolution (print quality)
    print(f"Saving high-resolution figure to {output_file}...")
    plt.savefig(output_file, dpi=300)
    print("Done.")

if __name__ == "__main__":
    generate_issues_chart()
