freeze:
	@pip freeze > requirements.txt
dep:
	@pip list --format=freeze > requirements.txt