import torch
import torch.nn as nn
import torch.optim as optim
import csv
import os
import time

class RetrievalAdapter(nn.Module):
    def __init__(self, emb_dim=384):
        super().__init__()
        # [FINE TUNING] Adapts the frozen embeddings to our specific domain
        self.adapter = nn.Sequential(
            nn.Linear(emb_dim, emb_dim),
            nn.LayerNorm(emb_dim)
        )
    def forward(self, x):
        return x + self.adapter(x)

def main():
    print("[FINE TUNING] Starting Retrieval Model Fine-Tuning...")
    # Synthetic embeddings data simulating ChromaDB DefaultEmbeddingFunction
    X = torch.rand((100, 384))
    # Synthetic target to simulate contrastive loss fine-tuning alignment
    y = X + torch.randn((100, 384)) * 0.1

    model = RetrievalAdapter()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    os.makedirs(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results")), exist_ok=True)
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results", "fine_tuning_metrics.csv"))

    epochs = 30
    metrics = []
    
    start_time = time.time()
    for epoch in range(epochs):
        optimizer.zero_grad()
        out = model(X)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")
            metrics.append({"epoch": epoch + 1, "loss": loss.item()})
            
    print(f"[FINE TUNING] Completed in {time.time() - start_time:.2f}s")
    
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["epoch", "loss"])
        writer.writeheader()
        writer.writerows(metrics)
        
    print(f"Fine Tuning metrics saved to {csv_path}")
    
    # Save model weights
    model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models"))
    os.makedirs(model_dir, exist_ok=True)
    torch.save(model.state_dict(), os.path.join(model_dir, "retrieval_adapter.pth"))

if __name__ == "__main__":
    main()
