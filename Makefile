freeze:
	@pip freeze > requirements.txt
dep:
	@pip install -r requirements.txt