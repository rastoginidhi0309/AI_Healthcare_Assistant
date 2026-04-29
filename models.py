from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

RANDOM_STATE = 42

FEATURES = [
    "age",          # years
    "bmi",          # kg/m^2
    "glucose",      # mg/dL fasting
    "sys_bp",       # systolic mmHg
    "chol",         # total cholesterol mg/dL
    "smoker",       # 0/1
    "steps"         # daily steps (k)
]

@dataclass
class RiskModels:
    diabetes: Pipeline
    heart: Pipeline
    ckd: Pipeline

def _generate_synthetic(n=5000, seed=RANDOM_STATE):
    rng = np.random.default_rng(seed)
    age = rng.normal(45, 12, n).clip(18, 85)
    bmi = rng.normal(27, 5, n).clip(16, 50)
    glucose = rng.normal(100, 25, n).clip(60, 250)
    sys_bp = rng.normal(122, 15, n).clip(90, 200)
    chol = rng.normal(190, 35, n).clip(110, 320)
    smoker = rng.binomial(1, 0.28, n)
    steps = rng.normal(7, 3, n).clip(0.5, 20)

    X = np.column_stack([age, bmi, glucose, sys_bp, chol, smoker, steps])

    # Diabetes
    logit_diab = (-10 + 0.03*age + 0.15*bmi + 0.035*glucose + 0.01*sys_bp + 0.006*chol + 0.5*smoker - 0.10*steps
                  + rng.normal(0, 0.8, n))
    y_diab = (1 / (1 + np.exp(-logit_diab)) > 0.5).astype(int)

    # Heart disease
    logit_heart = (-9 + 0.04*age + 0.02*bmi + 0.015*glucose + 0.03*sys_bp + 0.01*chol + 0.7*smoker - 0.08*steps
                   + rng.normal(0, 0.8, n))
    y_heart = (1 / (1 + np.exp(-logit_heart)) > 0.5).astype(int)

    # CKD proxy (risk with age, bp, diabetes proxy via glucose)
    logit_ckd = (-8 + 0.035*age + 0.02*bmi + 0.02*glucose + 0.028*sys_bp + 0.006*chol + 0.3*smoker - 0.06*steps
                 + rng.normal(0, 0.8, n))
    y_ckd = (1 / (1 + np.exp(-logit_ckd)) > 0.5).astype(int)

    return X, y_diab, y_heart, y_ckd

def train_models(n_samples=5000) -> RiskModels:
    X, y_diab, y_heart, y_ckd = _generate_synthetic(n_samples)
    def make_pipe():
        return Pipeline([("scaler", StandardScaler()),
                         ("clf", LogisticRegression(max_iter=200, random_state=RANDOM_STATE))])
    m_diab = make_pipe().fit(X, y_diab)
    m_heart = make_pipe().fit(X, y_heart)
    m_ckd = make_pipe().fit(X, y_ckd)
    return RiskModels(diabetes=m_diab, heart=m_heart, ckd=m_ckd)

def predict_proba(models: RiskModels, features: dict[str, float]):
    x = np.array([[features["age"], features["bmi"], features["glucose"], features["sys_bp"],
                   features["chol"], features["smoker"], features["steps"]]])
    return {
        "diabetes": float(models.diabetes.predict_proba(x)[0,1]),
        "heart": float(models.heart.predict_proba(x)[0,1]),
        "ckd": float(models.ckd.predict_proba(x)[0,1])
    }
