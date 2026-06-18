#!/home/nguyenpq/Downloads/face-recognition-system/.venv/bin/python
import os
import sys
import shutil
import cv2
import face_recognition
import numpy as np
from pathlib import Path

DATA_DIR = "/var/lib/face-auth"

def init_user_dir(username):
    user_dir = Path(DATA_DIR) / username
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir

def add_face_webcam(username, num_samples=5):
    user_dir = init_user_dir(username)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Không thể mở webcam!")
        return False

    encodings_list = []
    existing_images = list(user_dir.glob("face_*"))
    idx = len(existing_images)
    captured = 0

    print(f"\n📸 Chuẩn bị chụp {num_samples} ảnh cho '{username}'.")
    print("   Nhấn [SPACE] để chụp, [Q] để huỷ.\n")

    while captured < num_samples:
        ret, frame = cap.read()
        if not ret:
            break

        display = frame.copy()
        h, w = display.shape[:2]
        cv2.putText(
            display,
            f"Captured: {captured}/{num_samples}  |  SPACE=chup  Q=huy",
            (10, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb, model="hog")
        for top, right, bottom, left in locations:
            cv2.rectangle(display, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.imshow("Dang ky khuon mat PAM", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            print("⚠️  Đã huỷ.")
            break

        if key == ord(" "):
            if not locations:
                print("   ⚠️  Không phát hiện khuôn mặt, thử lại!")
                continue

            encs = face_recognition.face_encodings(rgb, locations)
            if encs:
                idx += 1
                captured += 1
                img_path = user_dir / f"face_{idx}.jpg"
                cv2.imwrite(str(img_path), frame)
                encodings_list.append(encs[0])
                print(f"   ✅ Ảnh {captured}/{num_samples} đã lưu.")

    cap.release()
    cv2.destroyAllWindows()

    if encodings_list:
        enc_file = user_dir / "encodings.npy"
        new_encs = np.array(encodings_list)
        if enc_file.exists():
            existing = np.load(str(enc_file))
            new_encs = np.vstack([existing, new_encs])
        np.save(str(enc_file), new_encs)
        return True
    return False

def list_faces():
    data_path = Path(DATA_DIR)
    if not data_path.exists():
        print("Chưa có database.")
        return
    
    print("\nDanh sách khuôn mặt đã đăng ký:")
    for user_dir in data_path.iterdir():
        if user_dir.is_dir():
            enc_file = user_dir / "encodings.npy"
            n_enc = len(np.load(str(enc_file))) if enc_file.exists() else 0
            print(f" - {user_dir.name}: {n_enc} encodings")

def remove_face(username):
    user_dir = Path(DATA_DIR) / username
    if user_dir.exists():
        shutil.rmtree(user_dir)
        print(f"Đã xoá dữ liệu của user '{username}'.")
    else:
        print(f"Không tìm thấy dữ liệu của user '{username}'.")

def main():
    if os.geteuid() != 0:
        print("Vui lòng chạy lệnh bằng sudo!")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Sử dụng: face-auth [add|list|remove|test]")
        sys.exit(1)

    cmd = sys.argv[1]
    
    if cmd == "add":
        username = input("Nhập username Linux: ").strip()
        if username:
            add_face_webcam(username)
    elif cmd == "list":
        list_faces()
    elif cmd == "remove":
        username = input("Nhập username Linux cần xoá: ").strip()
        if username:
            remove_face(username)
    elif cmd == "test":
        username = input("Nhập username Linux cần test: ").strip()
        if username:
            import subprocess
            print("Đang chạy test (có 5s timeout)...")
            res = subprocess.run(["/usr/local/lib/face-auth/pam_face_auth.py", username])
            if res.returncode == 0:
                print("✅ Test thành công: Nhận diện đúng!")
            else:
                print("❌ Test thất bại: Không nhận diện được hoặc timeout.")
    else:
        print("Lệnh không hợp lệ.")

if __name__ == "__main__":
    main()
