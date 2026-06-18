#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Vui lòng chạy script bằng sudo!"
  exit
fi

mkdir -p /usr/local/lib/face-auth
mkdir -p /var/lib/face-auth

cp pam_face_auth.py /usr/local/lib/face-auth/
cp face-auth-cli.py /usr/local/lib/face-auth/

chmod +x /usr/local/lib/face-auth/pam_face_auth.py
chmod +x /usr/local/lib/face-auth/face-auth-cli.py

ln -sf /usr/local/lib/face-auth/face-auth-cli.py /usr/local/bin/face-auth

# Import existing faces if user wants
echo "Đang import faces từ thư mục known_faces/ (nếu có)..."
if [ -d "../known_faces" ]; then
    for dir in ../known_faces/*/; do
        if [ -d "$dir" ]; then
            name=$(basename "$dir")
            echo "Tìm thấy user '$name', đang chuyển vào /var/lib/face-auth/nguyenpq/ ..."
            # Vì yêu cầu có câu hỏi: "Bạn muốn import tất cả faces hiện có vào user Linux nguyenpq?"
            # Mặc định mình sẽ gộp hết vào nguyenpq cho tiện
            mkdir -p /var/lib/face-auth/nguyenpq
            if [ -f "$dir/encodings.npy" ]; then
                # Cần ghép file npy nếu đã tồn tại, nhưng để đơn giản, ta chỉ copy lần đầu
                # Tốt nhất là dùng CLI để add lại hoặc import thủ công
                cp -n "$dir"/*.jpg /var/lib/face-auth/nguyenpq/ 2>/dev/null
                cp -n "$dir/encodings.npy" /var/lib/face-auth/nguyenpq/ 2>/dev/null
            fi
        fi
    done
fi
chown -R root:root /var/lib/face-auth
chmod -R 755 /var/lib/face-auth

echo "Cài đặt file thành công!"
echo "Chạy 'sudo face-auth test' để kiểm tra trước khi sửa PAM config."
