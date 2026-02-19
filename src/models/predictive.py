"""Predictive modeling: logistic/probit regression for survival and return prediction."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, precision_recall_curve, classification_report, roc_curve
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm


DEFAULT_FEATURES = [
    "sniper_count",
    "bundler_count",
    "insider_count",
    "dev_held_pct",
    "buy_count_1h",
    "sell_count_1h",
    "holders",
    "log_liquidity",
    "log_volume_24h",
    "wallet_age_avg",
    "buy_sell_ratio_1h",
]


class PredictiveModel:
    """Predict meme coin outcomes from first-hour features."""

    def __init__(self, panel_df: pd.DataFrame):
        self.df = panel_df.copy()
        self.logit_result = None
        self.probit_result = None
        self.sklearn_model = None
        self.scaler = StandardScaler()

    def prepare_data(
        self,
        target: str = "survived_7d",
        features: list[str] | None = None,
        train_months: int = 4,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Prepare train/test split based on time (first N months train, rest test).

        Args:
            target: Binary outcome column.
            features: Feature columns to use.
            train_months: Number of months for training.

        Returns:
            X_train, X_test, y_train, y_test DataFrames.
        """
        if features is None:
            features = DEFAULT_FEATURES

        available = [f for f in features if f in self.df.columns]
        model_df = self.df[available + [target, "created_at"]].dropna()

        # Time-based split
        sorted_df = model_df.sort_values("created_at")
        split_point = int(len(sorted_df) * (train_months / 6))

        train = sorted_df.iloc[:split_point]
        test = sorted_df.iloc[split_point:]

        X_train = train[available]
        X_test = test[available]
        y_train = train[target].astype(int)
        y_test = test[target].astype(int)

        return X_train, X_test, y_train, y_test

    def fit_logistic_statsmodels(
        self,
        target: str = "survived_7d",
        features: list[str] | None = None,
    ) -> sm.Logit:
        """Fit logistic regression using statsmodels (for coefficients and p-values)."""
        if features is None:
            features = DEFAULT_FEATURES

        available = [f for f in features if f in self.df.columns]
        model_df = self.df[available + [target]].dropna()

        X = sm.add_constant(model_df[available])
        y = model_df[target].astype(int)

        logit = sm.Logit(y, X)
        self.logit_result = logit.fit(disp=0, maxiter=100)
        return self.logit_result

    def fit_probit_statsmodels(
        self,
        target: str = "survived_7d",
        features: list[str] | None = None,
    ) -> sm.Probit:
        """Fit probit regression as robustness check."""
        if features is None:
            features = DEFAULT_FEATURES

        available = [f for f in features if f in self.df.columns]
        model_df = self.df[available + [target]].dropna()

        X = sm.add_constant(model_df[available])
        y = model_df[target].astype(int)

        probit = sm.Probit(y, X)
        self.probit_result = probit.fit(disp=0, maxiter=100)
        return self.probit_result

    def fit_sklearn_logistic(
        self,
        target: str = "survived_7d",
        features: list[str] | None = None,
        train_months: int = 4,
    ) -> dict:
        """Fit sklearn logistic regression with train/test evaluation.

        Returns:
            Dict with AUC, precision, recall, classification report, ROC curve data.
        """
        X_train, X_test, y_train, y_test = self.prepare_data(target, features, train_months)

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        model = LogisticRegression(max_iter=1000, random_state=42)
        model.fit(X_train_scaled, y_train)
        self.sklearn_model = model

        # Predictions
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        y_pred = model.predict(X_test_scaled)

        # Metrics
        auc = roc_auc_score(y_test, y_pred_proba)
        fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
        precision, recall, pr_thresholds = precision_recall_curve(y_test, y_pred_proba)
        report = classification_report(y_test, y_pred, output_dict=True)

        # Feature importance (odds ratios from unscaled model)
        feature_names = X_train.columns.tolist()
        coefs = model.coef_[0]
        odds_ratios = np.exp(coefs)

        return {
            "auc": auc,
            "classification_report": report,
            "roc_curve": {"fpr": fpr, "tpr": tpr, "thresholds": thresholds},
            "pr_curve": {"precision": precision, "recall": recall},
            "feature_importance": pd.DataFrame({
                "feature": feature_names,
                "coefficient": coefs,
                "odds_ratio": odds_ratios,
            }).sort_values("odds_ratio", ascending=False),
            "n_train": len(y_train),
            "n_test": len(y_test),
            "train_positive_rate": y_train.mean(),
            "test_positive_rate": y_test.mean(),
        }

    def logistic_summary_table(self) -> pd.DataFrame:
        """Extract publication-ready logistic regression coefficients."""
        if self.logit_result is None:
            raise ValueError("Must fit logistic model first")

        summary = self.logit_result.summary2().tables[1]
        summary["odds_ratio"] = np.exp(summary["Coef."])
        summary["or_lower"] = np.exp(summary["Coef."] - 1.96 * summary["Std.Err."])
        summary["or_upper"] = np.exp(summary["Coef."] + 1.96 * summary["Std.Err."])

        return summary
