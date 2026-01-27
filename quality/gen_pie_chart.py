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

    # 2. Extract unique languages
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

    # 3. Setup Figure
    # CHANGE 1: WIDER FIGURE
    # We use (7 * n) for width and (5 * n) for height.
    # This extra width provides room for the legends on the right of each pie.
    fig, axes = plt.subplots(n, n, figsize=(7 * n, 5 * n))
    
    # CHANGE 2: INCREASE HORIZONTAL GAP
    # wspace=0.5 means the gap between charts is 50% of the chart width.
    # This ensures the legend text doesn't hit the chart next to it.
    plt.subplots_adjust(wspace=0.6, hspace=0.1)

    # 4. Iterate through the grid
    for i, target_lang in enumerate(lang_list):      # Row = Target
        for j, source_lang in enumerate(lang_list):  # Col = Source
            
            ax = axes[i, j] if n > 1 else axes
            key = f"{source_lang}_to_{target_lang}"
            
            # --- HEADERS ---
            if i == 0:
                ax.set_title(source_lang, fontsize=24, weight='bold', pad=20) 
            if j == 0:
                ax.set_ylabel(target_lang, fontsize=24, weight='bold', rotation=90, labelpad=20)

            # --- PLOTTING LOGIC ---
            if source_lang == target_lang:
                # Transparent Diagonal
                ax.set_facecolor('none')
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)
                ax.grid(False)

            elif key in data:
                issues = data[key]
                labels = [item['topic'] for item in issues]
                counts = [item['count'] for item in issues]
                
                # Pie Chart
                wedges, texts, autotexts = ax.pie(
                    counts, 
                    autopct='%1.0f%%',
                    startangle=90,
                    radius=0.9, 
                    pctdistance=0.85,
                    textprops={'fontsize': 14} 
                )
                
                # CHANGE 3: LEGEND POSITIONING
                # bbox_to_anchor=(1.0, 0.5) starts the legend exactly at the edge of the box.
                # The increased wspace (above) ensures this text has room to expand.
                ax.legend(
                    wedges, 
                    labels, 
                    title="Issues", 
                    loc="center left", 
                    bbox_to_anchor=(1.0, 0.5),
                    fontsize=14,
                    frameon=False 
                )
                ax.set_aspect('equal')
            else:
                # No Data Case
                ax.set_facecolor('none')
                ax.text(0.5, 0.5, "No Data", ha='center', va='center', color='#ccc', fontsize=14)
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)
                ax.grid(False)

    print(f"Saving high-resolution figure to {output_file}...")
    
    # Save with tight bounding box and transparency
    plt.savefig(output_file, dpi=300, bbox_inches='tight', transparent=True)
    print("Done.")

if __name__ == "__main__":
    generate_issues_chart()
