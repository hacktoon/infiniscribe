install:
	cp scripts/pre-commit.sh .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	pip install -r requirements.txt
	
install-dev: install
	pip install ipython ipdb

upgrade:
	pip install --upgrade pip -r requirements.txt

inspect:
	flake8 .

test:
	pytest --color=yes --cov --durations=3 --no-cov-on-fail -v

debug:
	pytest -s

