# Copyright Iterate Labs, Inc.
# Contact: jesper.kristensen@iteratelabs.co

echo "********************************************************"
echo "*       Welcome to BSAFE by Iterate Labs, Inc.         *"
echo "********************************************************"
# banner generated here: http://bagill.com/ascii-sig.php
echo ".______        _______.     ___       _______  _______"
echo "|   _  \      /       |    /   \     |   ____||   ____|"
echo "|  |_)  |    |   (----\`   /  ^  \    |  |__   |  |__"
echo "|   _  <      \   \      /  /_\  \   |   __|  |   __|"
echo "|  |_)  | .----)   |    /  _____  \  |  |     |  |____"
echo "|______/  |_______/    /__/     \__\ |__|     |_______|"
echo ""

# Set up the virtual environment from the pipfile:
# (see the Pipfile and Pipfile.lock):
echo "Setting up the Python environment for BSAFE"
pipenv shell
echo "Setting up Python..."
pipenv update
echo "[OK] Python has been set up."

echo "[ALL OK] BSAFE is ready for use."
echo

