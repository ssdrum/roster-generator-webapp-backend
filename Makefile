.PHONY: run

# Starts development server
run:
	uvicorn main:app --reload
