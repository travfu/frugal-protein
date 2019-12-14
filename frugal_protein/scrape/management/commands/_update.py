import os
import re
import subprocess
from datetime import date

from django.core.management import call_command

from frugal_protein import settings
from products.models import Brands, ProductInfo


def run_win_cmd(self, cmd):
        process =  subprocess.Popen(cmd,
                                    shell=True,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        return process


class UpdateLiveDB:
    """
    This class inserts filtered products from local development database to the
    local live development database. Products are filtered by their protein 
    content (per 100g). This is to keep the number of database rows below the 
    10,000 limit for Heroku's psql free tier (500 rows reserved for django 
    backend)

    Attributes
        max_rows (str): maximum rows that can be inserted into db 
        protein_threshold (int/float): protein threshold for filtering
        live_db (str): db name listed under settings.DATABASES
    """

    max_rows = 9500
    protein_threshold = 70  # per 100g/ml
    live_db = 'live'
    run_win_cmd = run_win_cmd
    
    def execute(self):
        self.reset_tables()

        # Get products greater than or equal to protein threshold
        candidate_products = ProductInfo.objects.filter(
            protein__gte=self.protein_threshold)
        products = candidate_products.filter(
            description__isnull=False,
            qty__isnull=False,
            protein__isnull=False
        )

        # Get brands found in filtered products
        brands = [p.brand for p in products]
        brands = set(brands)
        if None in brands:
            brands.remove(None)

        # Insert rows into live db
        total_rows = len(products) + len(brands)
        if total_rows <= self.max_rows:
            for brand in brands:
                brand.save(using=self.live_db)
            for product in products:
                product.save(using=self.live_db)
            print(f'{total_rows} inserted into local heroku db')
        else:
            msg = f'Too many rows! {total_rows}/{self.max_rows}'
            print(msg)
    
    def reset_tables(self):
        """ Reset (truncate) productinfo and brands table """
        # psql_user = os.getenv('PSQL_USER')
        # psql_pass = str.encode(os.getenv('PSQL_PW'))
        
        # # Enter psql shell
        # cmd = f'psql -U {psql_user}'
        # process = self.run_win_cmd(cmd)
        # process.stdin.write(psql_pass)

        # # Connect to local live db
        # connect_cmd = b'\c frugal_protein_local;'
        # process.stdin.write(connect_cmd)
        
        # tables = ['products_brands', 'products_productinfo']
        # truncate_cmd = f"TRUNCATE TABLE {', '.join(tables)};"
        # process.stdin.write(truncate_cmd)
        call_command('flush', '--database=live', '--noinput')
        while len(ProductInfo.objects.using('live').all()) == 0 and \
              len(Brands.objects.using('live').all()) == 0:
              return


class UpdateHeroku:
    """ Manually update psql on Heroku's servers via pg_dump and pg_restore """
    # pg_dump & pg_restore is used instead of 'heroku pg:push' because I can't 
    # get this pg:push to work on windows (problem relating to PGUSER=root 
    # password prompt)
    run_win_cmd = run_win_cmd


    def execute(self):
        filename = f'{date.today()}3.dump'
        path = os.path.join(settings.BASE_DIR, 'scrape', 'db_dumps', filename)
        local_livedb = settings.DATABASES['live']['NAME']
        self.dump_local(local_livedb, path)

        while not os.path.isfile(path):
            # Wait until local dump file has completed saving
            pass

        db_config = self.get_db_config()
        self.restore_heroku(db_config, path)
    

    # def run_win_cmd(self, cmd):
    #     return subprocess.Popen(cmd,
    #                             shell=True,
    #                             stdin=subprocess.PIPE,
    #                             stdout=subprocess.PIPE,
    #                             stderr=subprocess.PIPE)

    def dump_local(self, db_name, filename):
        psql_user = os.getenv('PSQL_USER')
        psql_pass = str.encode(os.getenv('PSQL_PW'))  # str > bytes
        cmd = f'pg_dump --verbose -F c -Z 0 -U {psql_user} -h localhost -p 5432 {db_name} > {filename}'
        print(cmd)
        process = self.run_win_cmd(cmd)
        process.stdin.write(psql_pass)
        process.stdin.flush()

    def get_db_config(self):
        # pattern: postgres://<username>:<password>@<hostname>:<port>/<db_name>
        cmd = 'heroku config:get DATABASE_URL --app frugal-protein'
        process = self.run_win_cmd(cmd)
        res = [line for line in process.stdout]
        if len(res) == 1 and str(res[0]).startswith("b'postgres"):
            regex = "b'postgres:\/\/(\w+):(\w+)@(.+):(\d+)\/(\w+)"
            matches = re.findall(regex, str(res[0]))
            config = {
                'username': matches[0][0],
                'password': matches[0][1],
                'hostname': matches[0][2],
                'port': matches[0][3],
                'db_name': matches[0][4]
            }
            return config
        raise ValueError('Error retrieving db config')

    def restore_heroku(self, db_config, filename):
        user = db_config['username']
        pw = db_config['password']
        host = db_config['hostname']
        port = db_config['port']
        db = db_config['db_name']
        cmd = f'pg_restore --verbose --no-acl --no-owner -U {user} -h {host} -p {port} -d {db} < {filename}'
        process = self.run_win_cmd(cmd)
        process.stdin.write(pw)
