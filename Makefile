freeze:
	@pip list --format=freeze > requirements.txt
dep:
	@pip install -r requirements.txt