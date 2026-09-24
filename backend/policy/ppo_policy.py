import os
import numpy as np
from pathlib import Path
from typing import Tuple, List
from backend.config import settings, BASE_DIR

CHECKPOINT_DIR = BASE_DIR / settings.policy.checkpoint_dir
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_PATH = CHECKPOINT_DIR / "latest.pt"


class PolicyNetwork:
    """3-layer PyTorch MLP policy network over 9-dim state vector -> 3 action logits."""
    def __init__(self, state_dim: int = 9, action_dim: int = 3):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.torch_available = False
        self.model = None

        try:
            import torch
            import torch.nn as nn

            class MLPPolicy(nn.Module):
                def __init__(self, in_dim, out_dim):
                    super().__init__()
                    self.net = nn.Sequential(
                        nn.Linear(in_dim, 32),
                        nn.ReLU(),
                        nn.Linear(32, 32),
                        nn.ReLU(),
                        nn.Linear(32, out_dim)
                    )

                def forward(self, x):
                    return self.net(x)

            self.MLPPolicyClass = MLPPolicy
            self.model = MLPPolicy(state_dim, action_dim)
            self.torch_available = True
            self._load_checkpoint()
        except Exception as e:
            print(f"[PolicyNetwork] PyTorch load notice ({e}). Using deterministic rule policy.")

    def _load_checkpoint(self):
        if self.torch_available and CHECKPOINT_PATH.exists():
            try:
                import torch
                state_dict = torch.load(CHECKPOINT_PATH, map_location="cpu")
                self.model.load_state_dict(state_dict)
                self.model.eval()
                print(f"[PolicyNetwork] Loaded trained PPO policy checkpoint from {CHECKPOINT_PATH}")
            except Exception as e:
                print(f"[PolicyNetwork] Error loading checkpoint ({e}). Using default initialized weights.")

    def predict_action(self, state: np.ndarray) -> Tuple[int, str, List[float]]:
        if self.torch_available and self.model is not None:
            import torch
            with torch.no_grad():
                tensor_state = torch.FloatTensor(state).unsqueeze(0)
                logits = self.model(tensor_state)
                probs = torch.softmax(logits, dim=-1).squeeze(0).tolist()
                action = int(torch.argmax(logits, dim=-1).item())

            action_names = ["ANSWER", "RETRIEVE_MORE", "ABSTAIN"]
            return action, action_names[action], probs
        else:
            # Rule fallback
            entropy = float(state[0])
            max_sim = float(state[3])
            retrieval_round = int(state[6] * 3.0)
            if entropy < 0.25 and max_sim > 0.6:
                return 0, "ANSWER", [0.8, 0.1, 0.1]
            elif retrieval_round < 3 and (entropy >= 0.25 or max_sim <= 0.6):
                return 1, "RETRIEVE_MORE", [0.1, 0.8, 0.1]
            else:
                return 2, "ABSTAIN", [0.1, 0.1, 0.8]


_policy_instance = None

def get_policy_network() -> PolicyNetwork:
    global _policy_instance
    if _policy_instance is None:
        _policy_instance = PolicyNetwork()
    return _policy_instance
