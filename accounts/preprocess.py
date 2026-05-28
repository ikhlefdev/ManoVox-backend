import numpy as np

MAX_FRAMES = 64
N_LM = 114
INPUT_DIM = N_LM * 9  # 1026
LHAND_S, RHAND_S = 62, 83


def dominant_hand_normalize(seq: np.ndarray) -> np.ndarray:
    """
    seq: (64, 114, 3) — raw landmarks from Flutter
    """
    seq = seq.copy()
    lh = seq[:, LHAND_S:RHAND_S, :]
    rh = seq[:, RHAND_S:104, :]

    l_present = (~np.isnan(lh[:, 0, 0])).sum()
    r_present = (~np.isnan(rh[:, 0, 0])).sum()

    # Mirror if left hand is dominant
    if l_present > r_present:
        seq[:, :, 0] = 1.0 - seq[:, :, 0]

    # Normalize by left hand span (wrist to middle finger tip)
    wrist = seq[:, LHAND_S:LHAND_S + 1, :]
    tip = seq[:, LHAND_S + 12:LHAND_S + 13, :]
    span = np.linalg.norm(tip - wrist, axis=2, keepdims=True)
    span = np.where(span < 1e-6, 1.0, span)

    valid = ~np.isnan(wrist[:, 0, 0])
    seq[valid] = (seq[valid] - wrist[valid]) / span[valid]
    np.nan_to_num(seq, copy=False, nan=0.0)
    return seq


def add_motion(seq: np.ndarray) -> np.ndarray:
    """
    Concatenates position, velocity, acceleration.
    """
    vel = np.zeros_like(seq)
    acc = np.zeros_like(seq)
    vel[1:] = seq[1:] - seq[:-1]
    acc[2:] = vel[2:] - vel[1:-1]
    return np.concatenate([seq, vel, acc], axis=-1)  # (64, 114, 9)


def preprocess(sequence: np.ndarray) -> np.ndarray:
    """
    sequence: (64, 114, 3) from Flutter
    returns: (64, 1026) ready for model
    """
    seq = dominant_hand_normalize(sequence)
    seq = add_motion(seq)
    return seq.reshape(MAX_FRAMES, INPUT_DIM).astype(np.float32)
