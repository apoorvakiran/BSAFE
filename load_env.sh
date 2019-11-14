# -------------------------------------------
# Copyright Iterate Labs, Inc.
# Contact: jesper.kristensen@iteratelabs.co
# -------------------------------------------

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

echo "Setting up the Data Store script..."
first_line=$(head -n 1 scripts/data_store.py)
if [[ $first_line == "#"* ]]
then
	tail -n +2 scripts/data_store.py > data_store.tmp && mv data_store.tmp scripts/data_store.py
fi
echo -e "#"'!'"`which python`\n$(cat scripts/data_store.py)" > scripts/data_store.py
pipenv run python scripts/data_store.py > /dev/null
echo "[OK] Data Store script set up"

echo "[ALL OK] >> BSAFE is ready for use <<"
echo

