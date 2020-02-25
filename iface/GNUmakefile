include conf/local.mk

.DEFAULT_GOAL := help

WEB             ?= ${ROOT}/web
PROTOS		?= ${ROOT}/protos
CONFIG		?= ${ROOT}/conf
LOGS		?= ${ROOT}/logs
HTTPD_USER	?= ${OWNER}
HTTPD_GROUP	?= ${OWNER_GROUP}
HTTPD_LOGS	?= ${ROOT}/logs
MAKE		?= make

help:
	@echo '\
	Avalible targets:\
	*	init		- Build configs based on conf/local.mk;\
	*	configs		- Link configs to system directories;\
				  (Linux by default)\
	*	configs-freebsd	- Link configs to FreeBSD system directories;\
	*	configs-linux	- Link configs to Linux system directories;\
		\
		updateall	- Update project from repo;\
		\
	Targets marked by "*" need superuser privileges!\
	'

configs: configs-linux

configs-freebsd: build_protos
	@mkdir -p /usr/local/etc/nginx/sites-enabled
	@ln -s ${CONFIG}/nginx.conf /usr/local/etc/nginx/sites-enabled/draftdesign-iface.conf

configs-linux: build_protos
	@mkdir -p /etc/nginx/sites-enabled
	@ln -s ${CONFIG}/nginx.conf /etc/nginx/sites-enabled/draftdesign-iface.conf



updateall:
	@sh -c 'scripts/projectupdate.sh;'



init: build_protos
#	${call build_exec}

compat_links:
#	@sh -c "ln -s ${CONF} ${SQLINSTALL}/ >/dev/null 2>/dev/null; \
#	ln -s ${CONF} ${CRONSC}/ >/dev/null 2>&1; \
#	mkdir -p ${PROJECTLIBS}/${DB_TABLEPREFIX}db >/dev/null 2>&1; \
#	rm ${PROJECTLIBS}/${DB_TABLEPREFIX}db/* >/dev/null 2>&1; \
#	ln -s ${PROJECTLIBS}/dbsrc/* ${PROJECTLIBS}/${DB_TABLEPREFIX}db/ >/dev/null 2>&1; "

build_protos: make_dirs compat_links 
	${call build, ${PROTOS}/nginx.conf, ${CONFIG}/nginx.conf}
	${call build, ${PROTOS}/urls.js, ${WEB}/js/urls.js}


make_dirs:
	@mkdir -p ${PROTOS} 2>/dev/null
	@mkdir -p ${CONFIG} 2>/dev/null
	@mkdir -p ${LOGS} 2>/dev/null
	@chown -R ${OWNER} ${ROOT}
	@chown -R ${HTTPD_USER}:${HTTPD_GROUP} ${LOGS} 

define build_exec
	${call build, ${1}, ${2}} && chmod a+x ${2}
endef


define build
	@sed \
		-e 's%@ROOT@%${ROOT}%g' \
		-e 's%@CONFIG@%${CONFIG}%g' \
		-e 's%@PROTOS@%${PROTOS}%g' \
		-e 's%@LOGS@%${LOGS}%g' \
		-e 's%@HTTPD_USER@%${HTTPD_USER}%g' \
		-e 's%@HTTPD_HOST@%${HTTPD_HOST}%g' \
		-e 's%@HTTPD_LOGS@%${HTTPD_LOGS}%g' \
		-e 's%@WS_URL@%${WS_URL}%g' \
		-e 's%@API_URL@%${API_URL}%g' \
		-e 's%@PASSPORT_URL@%${API_URL}%g' \
		-e 's%@WEB@%${WEB}%g' \
		-e 's%@OWNER@%${OWNER}%g' \
		-e 's%@MAKE@%${MAKE}%g' \
	< ${1} > ${2}
endef
