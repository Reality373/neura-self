#!/bin/bash

# Termux Auto-Installer for Neura-Self
echo "=========================================="
echo "    Neura-Self Termux Setup Script        "
echo "=========================================="

echo "[1/4] Updating package lists..."
pkg update -y
pkg upgrade -y

echo "[2/4] Installing required dependencies..."
# build-essential and binutils are required for compiling python modules on ARM
pkg install python git build-essential binutils termux-api -y

echo "[3/4] Requesting storage permissions..."
echo "--> PLEASE CLICK 'ALLOW' ON YOUR PHONE POPUP <--"
termux-setup-storage

echo "[4/4] Installing Python requirements..."
pip install -r requirements.txt

echo "=========================================="
echo "    Setup Complete!                       "
echo "    To start the bot, run: python main.py "
echo "=========================================="
