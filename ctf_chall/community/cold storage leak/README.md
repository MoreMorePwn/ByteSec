# Template Challenge

Gunakan template ini untuk membuat challenge baru. Copy seluruh folder ini ke kategori yang sesuai dan rename sesuai nama challenge.

## Struktur Folder

```
Challenge-Name/
├── challenge.yml          # Konfigurasi CTFd
├── README.md              # Writeup (step-by-step)
├── dist/
│   └── dist.zip           # File yang diberikan ke peserta
└── src/
    ├── Dockerfile          # Docker image untuk challenge
    ├── docker-compose.yml  # Docker compose config
    ├── start.sh            # Script untuk deploy container
    ├── run.sh              # Wrapper eksekusi binary
    ├── chall.c             # Source code challenge
    ├── flag.txt            # Flag file
    └── xinetd.conf         # Konfigurasi xinetd (service + logging + limits)
```

## Setup Guide

### 1. Copy Template

```bash
cp -r Template-Challenge/ "Binary Exploitation/Nama Challenge Baru"
```

### 2. Edit `challenge.yml`

| Field             | Keterangan                                                                                               |
| ----------------- | -------------------------------------------------------------------------------------------------------- |
| `name`            | Nama challenge yang tampil di CTFd                                                                       |
| `category`        | Salah satu: `Binary Exploitation`, `Web Exploitation`, `Cryptography`, `Forensic`, `Reverse Engineering` |
| `description`     | Deskripsi challenge (support HTML)                                                                       |
| `connection_info` | Format: `nc 103.185.52.198 {port}` atau URL untuk web                                                    |
| `flags`           | Flag challenge, format: `PETIR{...}`                                                                     |
| `tags`            | Pilih **satu** difficulty: `baby`, `easy`, `medium`, `hard`                                              |
| `files`           | File distribusi: `dist/dist.zip`                                                                         |
| `state`           | `hidden` (belum rilis) atau `visible` (sudah rilis)                                                      |

> **DON'T CHANGE** — Jangan ubah bagian `value`, `type`, `extra` (scoring dinamis).

### 3. Edit Source Code

1. Tulis challenge di `src/chall.c`
2. Pastikan ada `setvbuf` di `setup()` agar I/O tidak di-buffer
3. Compile dengan flag yang diinginkan:

```bash
# Contoh: tanpa stack protector, no PIE
gcc -o chall chall.c \
    -fno-stack-protector \
    -no-pie \
    -Wl,-z,relro,-z,now

# Contoh: dengan semua proteksi
gcc -fstack-protector-strong -fPIE -pie \
    -Wl,-z,relro -Wl,-z,now -Wl,-z,noexecstack \
    -o chall chall.c
```

### 4. Edit Flag

Ganti isi `src/flag.txt` dengan flag yang benar:

```
PETIR{flag_sesuai_challenge}
```

### 5. Edit `src/Dockerfile`, `run.sh`, dan `xinetd.conf`

Template ini sudah pakai **xinetd** dengan single config file.
Default path di template pakai `/home/nama_user`. Ganti semua instance `nama_user` (username dan path) dengan nama yang sesuai:

**File yang perlu diedit:**

| File | Yang diganti |
| --- | --- |
| `Dockerfile` | `nama_user` → `{nama_user}` di semua COPY dan RUN |
| `run.sh` | Path binary: `cd /home/{nama_user} && ./chall` |
| `xinetd.conf` | `service chall` → `service {nama_service}`, `user = nama_user` → `user = {nama_user}`, `server = /home/nama_user/run` → `server = /home/{nama_user}/run` |

**Konfigurasi xinetd.conf:**

```
service nama_service
{
    disable         = no
    type            = UNLISTED
    protocol        = tcp
    socket_type     = stream
    port            = 3134          # Port internal (mapped via docker-compose)
    bind            = 0.0.0.0
    wait            = no
    user            = nama_user     # Sesuaikan dengan user di Dockerfile
    server          = /home/nama_user/run
    log_type        = FILE /var/log/xinetdlog
    log_on_success  = HOST PID
    log_on_failure  = HOST
    per_source      = 10            # Max koneksi per IP
    rlimit_cpu      = 20            # Max CPU time (detik)
    rlimit_as       = 128M          # Max virtual memory
    cps             = 25 30         # Max 25 conn/s, cooldown 30s
}
```

### 6. Edit `src/docker-compose.yml`

```yaml
services:
  nama-challenge: # Ganti dengan nama challenge (lowercase, kebab-case)
    image: nama-challenge # Sama dengan service name
    build: .
    restart: always
    mem_limit: 128m
    cpus: 0.25 # 0.25 untuk pwn biasa, 1.0 untuk QEMU
    environment:
      - TERM=xterm
    ports:
      - "{external_port}:3134" # Port eksternal harus unik, internal actually bebas
```

**Resource limits:**
| Tipe Challenge | Memory | CPU |
|---------------|--------|-----|
| Standard pwn (xinetd) | `128m` | `0.25` |
| Web challenge | `256m` | `0.25` |
| QEMU/Kernel | `1g` | `1.0` |

### 7. Buat dist.zip

Masukkan file yang akan diberikan ke peserta (binary, source code jika perlu) ke dalam `dist/dist.zip`.

### 8. Deploy

```bash
cd src/
bash start.sh
```

Ini akan menjalankan `docker compose down` lalu `docker compose up --build -d --force-recreate`.

### 9. Test

```bash
nc 103.185.52.198 {external_port}
```

Pastikan challenge berjalan dan flag bisa didapatkan.

## Ref
