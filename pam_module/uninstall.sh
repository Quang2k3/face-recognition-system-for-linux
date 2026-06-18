#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Vui lòng chạy script bằng sudo!"
  exit
fi

echo "Đang gỡ cài đặt custom PAM face-auth..."

rm -f /usr/local/bin/face-auth
rm -rf /usr/local/lib/face-auth
# Xóa data nếu muốn, nhưng mình comment lại để an toàn
# rm -rf /var/lib/face-auth

echo "Khôi phục PAM config (xóa dòng pam_face_auth.py)..."
sed -i '/pam_face_auth.py/d' /etc/pam.d/sudo
sed -i '/pam_face_auth.py/d' /etc/pam.d/system-auth
sed -i '/pam_face_auth.py/d' /etc/pam.d/gdm-password

echo "Đã gỡ cài đặt xong!"
