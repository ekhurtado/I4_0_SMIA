FROM ekhurtado/smia:alpine-base-latest

#COPY operator_gui_logic.py /
#COPY smia_operator_starter.py /
COPY *.py /
COPY htmls /htmls

WORKDIR /

CMD ["python3", "-u", "smia_operator_starter.py"]