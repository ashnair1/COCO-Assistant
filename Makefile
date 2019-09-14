all:
	echo "Building coco_assistant"
	python setup.py sdist bdist_wheel
	pip install -e .
clean:
	pip uninstall -y coco-assistant
	rm -rf build dist *.egg-info
	echo "Rebuilding"
	python setup.py sdist bdist_wheel
