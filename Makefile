setup:
	pip3 install -r requirements.txt

pipeline:
	python3 load_data.py
	python3 analysis.py

dashboard:
	streamlit run dashboard.py

clean:
	rm -f teiko.db