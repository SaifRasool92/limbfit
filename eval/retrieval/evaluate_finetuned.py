import os
import matplotlib.pyplot as plt
import pandas as pd
from .baseline import evaluate

def main():
    test_file = os.path.join(os.path.dirname(__file__), "test.jsonl")
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models", "limbfit-embedder")
    
    if not os.path.exists(model_path):
        print(f"Fine-tuned model not found at {model_path}. Please run finetune.py first.")
        print("Note: Fine-tuning is currently skipped due to PyTorch environment constraints.")
        return

    # If we had the model, we would evaluate it here using a custom eval function
    # For now, it will exit above.
        
    out_csv = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "retrieval_finetuned.csv")
    with open(out_csv, 'w') as f:
        f.write("model,recall@1,recall@3,recall@5,mrr\n")
        f.write(f"limbfit-embedder,{metrics['recall@1']:.4f},{metrics['recall@3']:.4f},{metrics['recall@5']:.4f},{metrics['mrr']:.4f}\n")
    print(f"Saved results to {out_csv}")
    
    # Attempt to plot before/after
    baseline_csv = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "retrieval_baseline.csv")
    if os.path.exists(baseline_csv):
        try:
            df_base = pd.read_csv(baseline_csv)
            df_fine = pd.read_csv(out_csv)
            
            labels = ['Recall@1', 'Recall@3', 'Recall@5', 'MRR']
            base_vals = [df_base.iloc[0]['recall@1'], df_base.iloc[0]['recall@3'], df_base.iloc[0]['recall@5'], df_base.iloc[0]['mrr']]
            fine_vals = [df_fine.iloc[0]['recall@1'], df_fine.iloc[0]['recall@3'], df_fine.iloc[0]['recall@5'], df_fine.iloc[0]['mrr']]
            
            x = np.arange(len(labels))
            width = 0.35
            
            fig, ax = plt.subplots()
            ax.bar(x - width/2, base_vals, width, label='Baseline (bge-small-en-v1.5)')
            ax.bar(x + width/2, fine_vals, width, label='Fine-tuned (limbfit-embedder)')
            
            ax.set_ylabel('Scores')
            ax.set_title('Retrieval Performance Before and After Fine-Tuning')
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.legend()
            
            plot_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "retrieval_comparison.png")
            plt.savefig(plot_path)
            print(f"Saved plot to {plot_path}")
        except Exception as e:
            print(f"Could not generate plot: {e}")

if __name__ == "__main__":
    import numpy as np
    main()
