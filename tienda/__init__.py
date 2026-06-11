import pymysql
pymysql.install_as_MySQLdb()

# Saltar verificación de versión de MariaDB
import django.db.backends.mysql.base as mysql_base
mysql_base.DatabaseWrapper.is_mariadb = False