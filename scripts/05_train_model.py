#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: scripts/05_train_model.py
Mục đích: Huấn luyện Random Forest với dataset đã tạo
ĐÃ SỬA: 
- Thêm GridSearchCV để tìm tham số tốt nhất
- Thêm cross-validation
- Lưu cả model và best parameters
- So sánh kết quả trước và sau tuning
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
import joblib
import json
import os
import sys
from datetime import datetime

# === CẤU HÌNH ===
DATA_DIR = "/home/server-ubuntu/zeek_flow/data"
MODEL_DIR = "/home/server-ubuntu/zeek_flow/model"
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5  # Số folds cho cross-validation

# Tạo thư mục model
os.makedirs(MODEL_DIR, exist_ok=True)

print("=" * 60)
print("RANDOM FOREST TRAINING - WITH GRID SEARCH")
print("=" * 60)

# === ĐỌC DATASET ===
print("\n[1] Đọc dataset...")
dataset_path = f'{DATA_DIR}/dataset.csv'

if not os.path.exists(dataset_path):
    print(f"❌ Không tìm thấy {dataset_path}")
    print("   Chạy 04_feature_engineering.py trước")
    sys.exit(1)

df = pd.read_csv(dataset_path)
print(f"   ✅ Dataset shape: {df.shape}")
print(f"   📊 Columns: {list(df.columns)}")

# Kiểm tra phân phối label
print(f"\n   📊 Phân phối label:")
print(df['label'].value_counts())
print(f"   Attack ratio: {df['label'].mean()*100:.2f}%")

# === TÁCH FEATURES VÀ LABEL ===
print("\n[2] Tách features và label...")

# Bỏ cột timestamp (không dùng cho training)
X = df.drop(['timestamp', 'label'], axis=1)
y = df['label']

feature_names = list(X.columns)
print(f"   ✅ Features ({len(feature_names)}): {feature_names}")

# === CHIA TRAIN/TEST ===
print("\n[3] Chia train/test...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
)

print(f"   📊 Train size: {len(X_train)} ({len(X_train)/len(X)*100:.1f}%)")
print(f"   📊 Test size: {len(X_test)} ({len(X_test)/len(X)*100:.1f}%)")
print(f"   📊 Train attack ratio: {y_train.mean()*100:.2f}%")
print(f"   📊 Test attack ratio: {y_test.mean()*100:.2f}%")

# === HUẤN LUYỆN MODEL CƠ BẢN (KHÔNG TUNING) ===
print("\n[4] Huấn luyện Random Forest cơ bản...")

base_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight='balanced',
    random_state=RANDOM_STATE,
    n_jobs=-1
)

base_model.fit(X_train, y_train)

# Đánh giá model cơ bản
y_pred_base = base_model.predict(X_test)
y_pred_proba_base = base_model.predict_proba(X_test)[:, 1]

accuracy_base = accuracy_score(y_test, y_pred_base)
auc_base = roc_auc_score(y_test, y_pred_proba_base)

print(f"\n   📊 Kết quả model cơ bản:")
print(f"      - Accuracy: {accuracy_base:.4f}")
print(f"      - AUC-ROC: {auc_base:.4f}")

# Cross-validation cho model cơ bản
cv_scores_base = cross_val_score(base_model, X_train, y_train, cv=CV_FOLDS, scoring='f1')
print(f"      - CV F1 Score (mean): {cv_scores_base.mean():.4f} (+/- {cv_scores_base.std()*2:.4f})")

# === GRID SEARCH - TÌM THAM SỐ TỐT NHẤT ===
print("\n[5] Grid Search - Tìm tham số tối ưu...")

# Định nghĩa grid parameters
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [5, 10, 15, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['sqrt', 'log2', None]
}

print(f"   🔍 Grid search parameters:")
print(f"      - n_estimators: {param_grid['n_estimators']}")
print(f"      - max_depth: {param_grid['max_depth']}")
print(f"      - min_samples_split: {param_grid['min_samples_split']}")
print(f"      - min_samples_leaf: {param_grid['min_samples_leaf']}")
print(f"      - max_features: {param_grid['max_features']}")
print(f"\n   🔄 Tổng số combinations: {np.prod([len(v) for v in param_grid.values()])}")

# Tạo GridSearchCV object
rf = RandomForestClassifier(
    class_weight='balanced',
    random_state=RANDOM_STATE,
    n_jobs=-1
)

grid_search = GridSearchCV(
    estimator=rf,
    param_grid=param_grid,
    cv=CV_FOLDS,
    scoring='f1',  # Dùng F1 score vì dataset có thể imbalance
    n_jobs=-1,
    verbose=1,
    return_train_score=True
)

print("\n   🔄 Đang chạy Grid Search (có thể mất vài phút)...")
start_time = datetime.now()
grid_search.fit(X_train, y_train)
end_time = datetime.now()

print(f"\n   ✅ Grid Search hoàn tất sau: {end_time - start_time}")

# Kết quả grid search
print(f"\n   📊 Best parameters:")
for param, value in grid_search.best_params_.items():
    print(f"      - {param}: {value}")

print(f"\n   📊 Best cross-validation F1 score: {grid_search.best_score_:.4f}")

# === ĐÁNH GIÁ MODEL TỐI ƯU ===
print("\n[6] Đánh giá model tối ưu trên test set...")

best_model = grid_search.best_estimator_
y_pred = best_model.predict(X_test)
y_pred_proba = best_model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_pred_proba)

print(f"\n   📊 Kết quả model tối ưu:")
print(f"      - Accuracy: {accuracy:.4f}")
print(f"      - AUC-ROC: {auc:.4f}")

# So sánh với model cơ bản
print(f"\n   📊 So sánh cải thiện:")
print(f"      - Accuracy: {accuracy_base:.4f} → {accuracy:.4f} ({((accuracy-accuracy_base)/accuracy_base)*100:+.1f}%)")
print(f"      - AUC-ROC: {auc_base:.4f} → {auc:.4f} ({((auc-auc_base)/auc_base)*100:+.1f}%)")

# Classification Report
print("\n   📊 Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))

# Confusion Matrix
print("\n   📊 Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(cm)

# Tính các metrics từ confusion matrix
tn, fp, fn, tp = cm.ravel()
print(f"\n   📊 Detailed Metrics:")
print(f"      - True Positives (Attack detected): {tp}")
print(f"      - False Positives (False alarm): {fp}")
print(f"      - False Negatives (Missed attacks): {fn}")
print(f"      - True Negatives (Normal traffic): {tn}")
print(f"      - Precision: {tp/(tp+fp):.4f}")
print(f"      - Recall: {tp/(tp+fn):.4f}")
print(f"      - F1 Score: {2*tp/(2*tp+fp+fn):.4f}")

# === FEATURE IMPORTANCE ===
print("\n[7] Feature Importance Analysis...")

feature_imp = pd.DataFrame({
    'feature': feature_names,
    'importance': best_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n   📊 Top 10 features quan trọng nhất:")
print(feature_imp.head(10).to_string(index=False))

# Vẽ biểu đồ feature importance (text-based)
print("\n   📊 Feature Importance Distribution:")
for idx, row in feature_imp.head(10).iterrows():
    bar = '█' * int(row['importance'] * 50)
    print(f"      {row['feature'][:20]:20s} {bar} {row['importance']:.3f}")

# === LƯU MODEL VÀ KẾT QUẢ ===
print("\n[8] Lưu model và kết quả...")

# Lưu model
model_path = f'{MODEL_DIR}/rf_model_best.pkl'
joblib.dump(best_model, model_path)
print(f"   ✅ Model saved: {model_path}")

# Lưu feature list
feature_path = f'{MODEL_DIR}/feature_list.json'
with open(feature_path, 'w') as f:
    json.dump(feature_names, f)
print(f"   ✅ Features saved: {feature_path}")

# Lưu best parameters
params_path = f'{MODEL_DIR}/best_params.json'
with open(params_path, 'w') as f:
    json.dump(grid_search.best_params_, f, indent=4)
print(f"   ✅ Best parameters saved: {params_path}")

# Lưu kết quả đánh giá
results = {
    'accuracy': accuracy,
    'auc_roc': auc,
    'precision': tp/(tp+fp),
    'recall': tp/(tp+fn),
    'f1_score': 2*tp/(2*tp+fp+fn),
    'confusion_matrix': cm.tolist(),
    'best_params': grid_search.best_params_,
    'feature_importance': feature_imp.to_dict('records')
}

results_path = f'{MODEL_DIR}/evaluation_results.json'
with open(results_path, 'w') as f:
    json.dump(results, f, indent=4)
print(f"   ✅ Evaluation results saved: {results_path}")

# === LƯU MODEL CƠ BẢN ĐỂ SO SÁNH (TÙY CHỌN) ===
base_model_path = f'{MODEL_DIR}/rf_model_base.pkl'
joblib.dump(base_model, base_model_path)
print(f"   ✅ Base model saved: {base_model_path}")

# === TÓM TẮT KẾT QUẢ ===
print("\n" + "=" * 60)
print("TÓM TẮT KẾT QUẢ TRAINING")
print("=" * 60)
print(f"""
📊 Dataset:
   - Total samples: {len(df)}
   - Features: {len(feature_names)}
   - Attack ratio: {df['label'].mean()*100:.2f}%

🎯 Best Parameters:
""")
for param, value in grid_search.best_params_.items():
    print(f"   - {param}: {value}")

print(f"""
📈 Performance on Test Set:
   - Accuracy:  {accuracy:.4f}
   - Precision: {tp/(tp+fp):.4f}
   - Recall:    {tp/(tp+fn):.4f}
   - F1 Score:  {2*tp/(2*tp+fp+fn):.4f}
   - AUC-ROC:   {auc:.4f}

📊 Confusion Matrix:
   [{tn} {fp}]
   [{fn} {tp}]

🔍 Top 3 Features:
   1. {feature_imp.iloc[0]['feature']}: {feature_imp.iloc[0]['importance']:.3f}
   2. {feature_imp.iloc[1]['feature']}: {feature_imp.iloc[1]['importance']:.3f}
   3. {feature_imp.iloc[2]['feature']}: {feature_imp.iloc[2]['importance']:.3f}
""")

print("\n✅ TRAINING HOÀN TẤT!")
print("=" * 60)

# Gợi ý bước tiếp theo
print("\n👉 Bước tiếp theo:")
print("   Để chạy detection real-time:")
print("   sudo python3 scripts/06_detect_live.py")
print("\n   Để xem lại kết quả:")
print(f"   cat {MODEL_DIR}/evaluation_results.json")
