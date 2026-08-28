setup:
	pip install -r requirements.txt

pipeline:
	python load_data.py

dashboard:
	streamlit run dashboard.py

clean:
	rm -f teiko.db