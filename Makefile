pkls := $(patsubst ${CORPUS}/%.gz,%.counts.pkl,$(wildcard ${CORPUS}/*.gz))

all: counts.df.pkl

%.counts.pkl: ${CORPUS}/%.gz
	zcat $< | python cnt.py $@

counts.df.pkl: $(pkls)
	python join.py $* $@
