DEFAULT_DB_ALIAS = 'master'

SA_DATABASES = {
    'master': ['postgresql+psycopg2://@DB_MASTER@', 'w',],
    'slave': ['postgresql+psycopg2://@DB_SLAVE@', 'r',],
}

BLACKBOX_HOST = '@BLACKBOX_HOST@'
BLACKBOX_PORT = @BLACKBOX_PORT@

