# Amigo Invisible

App de sorteo de amigo invisible con parejas fijas y prohibidas.

## Correr en la compu (Windows)

Kivy 2.3.1 solo tiene versiones para Python 3.8 a 3.13, asi que hay que usar Python 3.13.

    py install 3.13
    py -3.13 -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python main.py

## Generar el APK (desde WSL / Ubuntu)

    cd "/mnt/c/Projects/amigo invisible"
    sudo apt update
    sudo apt install -y python3-pip python3-venv git zip unzip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses-dev libffi-dev libssl-dev build-essential
    python3 -m venv ~/venv-buildozer
    source ~/venv-buildozer/bin/activate
    pip install -r requirements-android.txt
    buildozer android debug

El APK queda en la carpeta `bin/`.
