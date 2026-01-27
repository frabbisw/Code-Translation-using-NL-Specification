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
    # We increase the figure size slightly to ensure text has room to breathe
    fig, axes = plt.subplots(n, n, figsize=(6 * n, 6 * n))
    
    # Adjust spacing: 
    # wspace=0.3 gives the legends on the right a bit more room before hitting the next chart
    plt.subplots_adjust(wspace=0.3, hspace=0.1)

    # 4. Iterate through grid
    for i, target_lang in enumerate(lang_list):      
        for j, source_lang in enumerate(lang_list):  
            
            ax = axes[i, j] if n > 1 else axes
            key = f"{source_lang}_to_{target_lang}"
            
            # --- HEADERS ---
            if i == 0:
                ax.set_title(source_lang, fontsize=22, weight='bold', pad=15)
            if j == 0:
                ax.set_ylabel(target_lang, fontsize=22, weight='bold', rotation=90, labelpad=15)

            # --- PLOTTING ---
            if source_lang == target_lang:
                # FIX 2: Minimalist N/A
                # Instead of big text, we just grey out the background
                ax.set_facecolor('#f0f0f0') # Light grey background
                ax.text(0.5, 0.5, "-", ha='center', va='center', color='#ccc', fontsize=20)
                
                # Hide ticks/spines cleanly
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)

            elif key in data:
                issues = data[key]
                labels = [item['topic'] for item in issues]
                counts = [item['count'] for item in issues]
                
                # FIX 3: Shrink pie radius (0.75) to make room for legend
                wedges, texts, autotexts = ax.pie(
                    counts, 
                    autopct='%1.0f%%',
                    startangle=90,
                    radius=0.75, 
                    pctdistance=0.75, # Move % numbers closer to center
                    textprops={'fontsize': 14}
                )
                
                # FIX 1: Legend adjustments
                ax.legend(
                    wedges, 
                    labels, 
                    title="Issues", 
                    loc="center left", 
                    # Anchor (1.0, 0.5) puts it exactly at the right edge of the pie area
                    bbox_to_anchor=(0.95, 0.5), 
                    fontsize=11,
                    frameon=False
                )
                ax.set_aspect('equal')
            else:
                # No Data - Subtle look
                ax.text(0.5, 0.5, "No Data", ha='center', va='center', color='grey', fontsize=12)
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)

    print(f"Saving high-resolution figure to {output_file}...")
    
    # --- CRITICAL FIX ---
    # bbox_inches='tight' calculates the bounding box of the figure *including* # all text and legends that might be sticking out, and expands the image to fit them.
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print("Done.")

if __name__ == "__main__":
    generate_issues_chart()
