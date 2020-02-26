include conf/local.mk

.DEFAULT_GOAL := help

WEB             ?= ${ROOT}/web
APPS            ?= ${WEB}/apps
PROTOS		?= ${ROOT}/protos
CONFIG		?= ${ROOT}/conf
LOGS		?= ${ROOT}/logs
GLOBALS		?= ${ROOT}/globals
MIGRATIONS      ?= ${GLOBALS}/migrations
SCRIPTS		?= ${ROOT}/scripts
SCRIPTS_CRON	?= ${SCRIPTS}/cron
SCRIPTS_TEST	?= ${SCRIPTS}/tests
HTTPD_USER	?= ${OWNER}
HTTPD_GROUP	?= ${OWNER_GROUP}
HTTPD_LOGS	?= ${ROOT}/logs
IDENT		?= itstructure
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
	*	restart		- Restart supervisord(FreeBSD);\
	*	rebsd		- Restart supervisord(FreeBSD);\
	*	relinux		- Restart supervisord(Linux);\
		\
		updateall	- Update project from repo;\
		\
	Targets marked by "*" need superuser privileges!\
	'

configs: configs-linux

configs-freebsd: build_protos
	@mkdir -p /usr/local/etc/supervisor
	@ln -s ${CONFIG}/supervisor.conf /usr/local/etc/supervisor/${IDENT}-${HTTPD_HOST}-api.conf
	@mkdir -p /usr/local/etc/nginx/sites-enabled
	@ln -s ${CONFIG}/nginx.conf /usr/local/etc/nginx/sites-enabled/${IDENT}-${HTTPD_HOST}-api.conf

configs-linux: build_protos
	@mkdir -p /etc/supervisor/conf.d
	@ln -s ${CONFIG}/supervisor.conf /etc/supervisor/conf.d/${IDENT}-${HTTPD_HOST}-api.conf
	@mkdir -p /etc/nginx/sites-enabled
	@ln -s ${CONFIG}/nginx.conf /etc/nginx/sites-enabled/${IDENT}-${HTTPD_HOST}-api.conf



restart: restart-freebsd
relinux: restart-linux
rebsd: restart-freebsd

restart-freebsd:
	@sh -c 'echo "Stoping..."; sudo /usr/local/etc/rc.d/supervisord stop; echo "sleeping 5 seconds..."; sleep 5;'
	@sh -c 'echo "Starting..."; sudo /usr/local/etc/rc.d/supervisord start;'

restart-linux:
	@sh -c 'echo "Stoping..."; sudo /etc/init.d/supervisor stop; echo "sleeping 5 seconds..."; sleep 5;'
	@sh -c 'echo "Starting..."; sudo /etc/init.d/supervisor start;'

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
	${call build, ${PROTOS}/supervisor.conf, ${CONFIG}/supervisor.conf}
	${call build, ${PROTOS}/nginx.conf, ${CONFIG}/nginx.conf}
	${call build, ${PROTOS}/gsettings.py, ${GLOBALS}/gsettings/local.py}
	${call build, ${PROTOS}/alembic.ini, ${GLOBALS}/alembic.ini}
	${call build, ${PROTOS}/start.py, ${APPS}/start.py}
	${call build, ${PROTOS}/api_settings.py, ${WEB}/settings/local.py}
	${call build, ${PROTOS}/py_path.py, ${SCRIPTS}/py_path.py}
	${call build, ${PROTOS}/py_path.py, ${SCRIPTS_CRON}/py_path.py}
	${call build, ${PROTOS}/py_path.py, ${SCRIPTS_TEST}/py_path.py}


make_dirs:
	@mkdir -p ${PROTOS} 2>/dev/null
	@mkdir -p ${CONFIG} 2>/dev/null
	@mkdir -p ${SCRIPTS_CRON} 2>/dev/null
	@mkdir -p ${SCRIPTS_TEST} 2>/dev/null
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
		-e 's%@GLOBALS@%${GLOBALS}%g' \
                -e 's%@MIGRATIONS@%${MIGRATIONS}%g' \
		-e 's%@SCRIPTS@%${SCRIPTS}%g' \
		-e 's%@SCRIPTS_CRON@%${SCRIPTS_CRON}%g' \
		-e 's%@SCRIPTS_TEST@%${SCRIPTS_TEST}%g' \
		-e 's%@ROOTCOOKIE@%${ROOTCOOKIE}%g' \
		-e 's%@HTTPD_USER@%${HTTPD_USER}%g' \
		-e 's%@HTTPD_HOST@%${HTTPD_HOST}%g' \
		-e 's%@HTTPD_LOGS@%${HTTPD_LOGS}%g' \
		-e 's%@BLACKBOX_HOST@%${BLACKBOX_HOST}%g' \
		-e 's%@BLACKBOX_PORT@%${BLACKBOX_PORT}%g' \
                -e 's%@REDIS_HOST@%${REDIS_HOST}%g' \
                -e 's%@REDIS_PORT@%${REDIS_PORT}%g' \
		-e 's%@DB_MASTER@%${DB_MASTER}%g' \
		-e 's%@DB_SLAVE@%${DB_SLAVE}%g' \
		-e 's%@WEB@%${WEB}%g' \
		-e 's%@APPS@%${APPS}%g' \
		-e 's%@OWNER@%${OWNER}%g' \
		-e 's%@MAKE@%${MAKE}%g' \
	< ${1} > ${2}
endef
