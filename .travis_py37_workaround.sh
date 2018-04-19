echo "The ready-made virtualenv is not the one we want. Deactivating..."
deactivate

echo "Installing 3.7 from deadsnakes..."
sudo apt-get --yes install python3.7

echo "Creating a fresh virtualenv. We can't use `ensurepip` because Debian."
python3.7 -m venv ~/virtualenv/python3.7-deadsnakes --without-pip
source ~/virtualenv/python3.7-deadsnakes/bin/activate

echo "We ensure our own pip."
curl -sSL https://bootstrap.pypa.io/get-pip.py | python3.7

echo
echo "Python version:"
python3.7 -c "import sys; print(sys.version)"
