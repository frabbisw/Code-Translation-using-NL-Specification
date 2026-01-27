import json
import matplotlib.pyplot as plt

def generate_issues_chart(json_file='tags.json', output_file='tags.png'):
    # 1. Load Data
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_file} not found.")
        return

    # 2. Extract languages
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
        return

    # 3. Setup Figure
    fig, axes = plt.subplots(n, n, figsize=(6 * n, 6 * n))
    
    # Adjust spacing
    plt.subplots_adjust(wspace=0.1, hspace=0.1)

    # 4. Iterate through grid
    for i, target_lang in enumerate(lang_list):      
        for j, source_lang in enumerate(lang_list):  
            
            ax = axes[i, j] if n > 1 else axes
            key = f"{source_lang}_to_{target_lang}"
            
            # --- HEADERS ---
            # Set titles on the first row/column even if the cell is empty/transparent
            if i == 0:
                ax.set_title(source_lang, fontsize=24, weight='bold', pad=20)
            if j == 0:
                ax.set_ylabel(target_lang, fontsize=24, weight='bold', rotation=90, labelpad=20)

            # --- PLOTTING LOGIC ---
            if source_lang == target_lang:
                # === TRANSPARENCY FIX ===
                
                # 1. Set background color to 'none' (Transparent)
                ax.set_facecolor('none') 
                
                # 2. Hide all ticks and labels
                ax.set_xticks([])
                ax.set_yticks([])
                
                # 3. Hide the border lines (spines)
                for spine in ax.spines.values():
                    spine.set_visible(False)
                
                # 4. Turn off the grid (just in case)
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
                
                # Legend
                ax.legend(
                    wedges, 
                    labels, 
                    title="Issues", 
                    loc="center left", 
                    bbox_to_anchor=(0.95, 0.5), 
                    fontsize=10,
                    frameon=False 
                )
                ax.set_aspect('equal')
            else:
                # No Data Case - Make this transparent too, but keep text? 
                # Or just vanish it completely. Let's vanish the box but keep text.
                ax.set_facecolor('none')
                ax.text(0.5, 0.5, "No Data", ha='center', va='center', color='#ccc', fontsize=12)
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)
                ax.grid(False)

    print(f"Saving high-resolution figure to {output_file}...")
    
    # === CRITICAL: Save with transparent=True ===
    plt.savefig(output_file, dpi=300, bbox_inches='tight', transparent=True)
    print("Done.")

if __name__ == "__main__":
    generate_issues_chart()
